// Implementation of "Controller", a primitive for simulation of statecharts.

use std::collections::BinaryHeap;
use std::collections::binary_heap;
use std::collections::HashMap;
use std::collections::hash_map;
use std::cmp::Ordering;
use std::cmp::Reverse;
use std::rc::Rc;
use std::rc::Weak;
use std::cell::Cell;

use crate::statechart::Timestamp;
use crate::statechart::Scheduler;
use crate::statechart::SC;

pub type TimerIndex = u16;

// Comparable part of QueueEntry
#[derive(Default, Copy, Clone, Ord, PartialOrd, PartialEq, Eq)]
struct EntryCmp {
  timestamp: Timestamp,

  // This field maintains FIFO order for equally timestamped entries.
  idx: TimerIndex,
}
pub struct QueueEntry<InEvent> {
  cmp: EntryCmp,
  canceled: Cell<bool>, // mutable, even if QueueEntry is immutable
  event: InEvent,
}

impl<InEvent> Ord for QueueEntry<InEvent> {
  fn cmp(&self, other: &Self) -> Ordering {
    self.cmp.cmp(&other.cmp)
  }
}
impl<InEvent> PartialOrd for QueueEntry<InEvent> {
  fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
    Some(self.cmp(other))
  }
}
impl<InEvent> PartialEq for QueueEntry<InEvent> {
  fn eq(&self, other: &Self) -> bool {
    self.cmp == other.cmp
  }
}
impl<InEvent> Eq for QueueEntry<InEvent> {}

pub struct Controller<InEvent> {
  simtime: Timestamp,

  // Queue entries allocated on the heap.
  // Reverse<T> turns BinaryHeap into a min-heap.
  queue: BinaryHeap<Reverse<Rc<QueueEntry<InEvent>>>>,

  // Counts number of entries per timestamp. To maintain FIFO order for equally-timestamped entries.
  idxs: HashMap<Timestamp, TimerIndex>,
}

impl<InEvent> Scheduler for Controller<InEvent> {
  type InEvent = InEvent;
  type TimerId = Weak<QueueEntry<InEvent>>;

  fn set_timeout(&mut self, delay: Timestamp, event: Self::InEvent) -> Self::TimerId {
    let timestamp = self.simtime + delay;
    let idx_ref = self.idxs.entry(timestamp).or_default();
    let idx = *idx_ref;
    *idx_ref += 1;
    let cmp = EntryCmp{ timestamp, idx };
    let entry = Rc::new(QueueEntry::<InEvent>{ cmp, event, canceled: Cell::new(false) });
    let weak = Rc::downgrade(&entry);
    self.queue.push(Reverse(entry));

    weak
  }
  fn unset_timeout(&mut self, weak: &Self::TimerId) {
    if let Some(strong) = weak.upgrade() {
      strong.canceled.set(true);
    }
  }
}

pub enum Until {
  Timestamp(Timestamp),
  Eternity,
}

impl<InEvent> Default for Controller<InEvent> {
  fn default() -> Self {
    Self {
      simtime: 0,
      queue: BinaryHeap::with_capacity(16),
      idxs: HashMap::<Timestamp, TimerIndex>::with_capacity(16),
    }
  }
}

impl<InEvent: Copy> Controller<InEvent> {
  // pub fn get_simtime(&self) -> Timestamp {
  //   self.simtime
  // }
  // pub fn get_earliest(&self) -> Until {
  //   match self.queue.peek() {
  //     None => Until::Eternity,
  //     Some(Reverse(entry)) => Until::Timestamp(entry.cmp.timestamp),
  //   }
  // }
  fn cleanup_idx(idxs: &mut HashMap<Timestamp, TimerIndex>, entry: &QueueEntry<InEvent>) {
    if let hash_map::Entry::Occupied(o) = idxs.entry(entry.cmp.timestamp) {
      if *o.get() == entry.cmp.idx+1 {
        o.remove_entry();
      }
    };
  }
  pub fn run_until<OutEvent>(&mut self, sc: &mut impl SC<InEvent=InEvent, OutEvent=OutEvent, Sched=Self>, until: Until, output: &mut impl FnMut(OutEvent)) -> (Timestamp, Until)
  {
    loop {
      let Reverse(entry) = if let Some(peek_mut) = self.queue.peek_mut() {
        let Reverse(ref entry) = *peek_mut;

        // Check if event was canceled
        if entry.canceled.get() {
          Self::cleanup_idx(&mut self.idxs, entry);
          binary_heap::PeekMut::pop(peek_mut);
          continue;
        }
        // Check if event too far in the future
        if let Until::Timestamp(t) = until {
          if entry.cmp.timestamp > t {
            return (self.simtime, until); // return next wakeup
          }
        };
        // OK, we'll handle the event
        Self::cleanup_idx(&mut self.idxs, entry);
        binary_heap::PeekMut::pop(peek_mut) // the return value of this call is the result of our 'if' expression :)
      } else {
        break;
      };

      // Handle event
      self.simtime = entry.cmp.timestamp;
      sc.big_step(Some(entry.event), self, output);
    };
    // Queue empty
    (self.simtime, Until::Eternity)
  }
}
