// Implementation of "Controller", a primitive for simulation of statecharts.

use std::collections::BinaryHeap;
use std::cmp::Ordering;
use std::cmp::Reverse;

use statechart::Timestamp;
use statechart::Scheduler;
use statechart::SC;
use statechart::OutEvent;

pub type TimerId = u16;

#[derive(Default, Copy, Clone, Ord, PartialOrd, PartialEq, Eq)]
pub struct EntryId {
  timestamp: Timestamp,

  // This field maintains FIFO order for equally timestamped entries.
  n: TimerId,
}

pub struct QueueEntry<InEvent> {
  id: EntryId,
  event: InEvent,
}
impl<InEvent> Ord for QueueEntry<InEvent> {
  fn cmp(&self, other: &Self) -> Ordering {
    self.id.cmp(&other.id)
  }
}
impl<InEvent> PartialOrd for QueueEntry<InEvent> {
  fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
    Some(self.cmp(other))
  }
}
impl<InEvent> PartialEq for QueueEntry<InEvent> {
  fn eq(&self, other: &Self) -> bool {
    self.id == other.id
  }
}
impl<InEvent> Eq for QueueEntry<InEvent> {}

// Right now, "removed" queue entries are put into a second BinaryHeap.
// This is not very efficient. Queue entries should be allocated on the heap,
// (preferrably using a pool allocator), and directly marked as "removed".
// Optionally, if the number of removed items exceeds a threshold, a sweep could remove "removed" entries.

pub struct Controller<InEvent> {
  simtime: Timestamp,
  next_id: TimerId,
  queue: BinaryHeap<Reverse<QueueEntry<InEvent>>>,
  removed: BinaryHeap<Reverse<EntryId>>,
}

impl<InEvent> Scheduler<InEvent, EntryId> for Controller<InEvent> {
  fn set_timeout(&mut self, delay: Timestamp, event: InEvent) -> EntryId {
    let id = EntryId{ timestamp: self.simtime + delay, n: self.next_id };
    let entry = QueueEntry::<InEvent>{ id, event };
    self.queue.push(Reverse(entry));
    self.next_id += 1; // TODO: will overflow eventually :(
    return id
  }
  fn unset_timeout(&mut self, id: EntryId) {
    self.removed.push(Reverse(id));
  }
}

pub enum Until {
  Timestamp(Timestamp),
  Eternity,
}

impl<InEvent: Copy> Controller<InEvent> {
  pub fn new() -> Self {
    Self {
      simtime: 0,
      next_id: 0,
      queue: BinaryHeap::with_capacity(8),
      removed: BinaryHeap::with_capacity(4),
    }
  }
  pub fn run_until<StatechartType: SC<InEvent, EntryId, Controller<InEvent>, OutputCallback>, OutputCallback: FnMut(OutEvent)>(&mut self, sc: &mut StatechartType, until: Until, output: &mut OutputCallback) {
    'running: loop {
      if let Some(Reverse(entry)) = self.queue.peek() {
        // Check if event was removed
        if let Some(Reverse(removed)) = self.removed.peek() {
          if entry.id == *removed {
            self.queue.pop();
            self.removed.pop();
            continue;
          }
        }
        // Check if event too far in the future
        if let Until::Timestamp(t) = until {
          if entry.id.timestamp > t {
            println!("break, timestamp {}, t {}", entry.id.timestamp, t);
            break 'running;
          }
        }
        // OK, handle event
        self.simtime = entry.id.timestamp;
        // eprintln!("time is now {}", self.simtime);
        sc.big_step(Some(entry.event), self, output);
        self.queue.pop();
      }
      else {
        break 'running;
      }
    }
  }
}
