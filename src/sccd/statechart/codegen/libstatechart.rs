use std::collections::BinaryHeap;
use std::cmp::Ordering;
use std::cmp::Reverse;


#[derive(Default)]
struct SameRoundLifeline<InternalType> {
  current: InternalType,
}

impl<InternalType: Default> SameRoundLifeline<InternalType> {
  fn current(&self) -> &InternalType {
    &self.current
  }
  fn raise(&mut self) -> &mut InternalType {
    &mut self.current
  }
  fn cycle(&mut self) {
    self.current = Default::default()
  }
}

#[derive(Default)]
struct NextRoundLifeline<InternalType> {
  one: InternalType,
  two: InternalType,

  one_is_current: bool,
}

impl<InternalType: Default> NextRoundLifeline<InternalType> {
  fn current(&self) -> &InternalType {
    if self.one_is_current { &self.one } else { &self.two }
  }
  fn raise(&mut self) -> &mut InternalType {
    if self.one_is_current { &mut self.two } else { &mut self.one }
  }
  fn cycle(&mut self) {
    if self.one_is_current {
      self.one = Default::default();
    } else {
      self.two = Default::default();
    }
    self.one_is_current = ! self.one_is_current
  }
}

// pub trait State<TimersType, ControllerType> {
//   // Execute enter actions of only this state
//   fn enter_actions(timers: &mut TimersType, c: &mut ControllerType);
//   // Execute exit actions of only this state
//   fn exit_actions(timers: &mut TimersType, c: &mut ControllerType);

//   // Execute enter actions of this state and its 'default' child(ren), recursively
//   fn enter_default(timers: &mut TimersType, c: &mut ControllerType);

//   // Execute enter actions as if the configuration recorded in this state is being entered
//   fn enter_current(&self, timers: &mut TimersType, c: &mut ControllerType);
//   // Execute exit actions as if the configuration recorded in this state is being exited
//   fn exit_current(&self, timers: &mut TimersType, c: &mut ControllerType);
// }

pub trait SC<EventType, ControllerType> {
  fn init(&mut self, c: &mut ControllerType);
  fn big_step(&mut self, event: Option<EventType>, c: &mut ControllerType);
}

type Timestamp = u32;
type TimerId = u16;

#[derive(Default, Copy, Clone, Ord, PartialOrd, PartialEq, Eq)]
pub struct EntryId {
  timestamp: Timestamp,
  n: TimerId,
}

pub struct QueueEntry<EventType> {
  id: EntryId,
  event: EventType,
}
impl<EventType> Ord for QueueEntry<EventType> {
  fn cmp(&self, other: &Self) -> Ordering {
    self.id.cmp(&other.id)
  }
}
impl<EventType> PartialOrd for QueueEntry<EventType> {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}
impl<EventType> PartialEq for QueueEntry<EventType> {
    fn eq(&self, other: &Self) -> bool {
        self.id == other.id
    }
}
impl<EventType> Eq for QueueEntry<EventType> {}

#[derive(Debug, Eq, PartialEq)]
pub struct OutEvent {
  port: &'static str,
  event: &'static str,
}

pub struct Controller<EventType, OutputCallback> {
  simtime: Timestamp,
  next_id: TimerId,
  queue: BinaryHeap<Reverse<QueueEntry<EventType>>>,
  removed: BinaryHeap<Reverse<EntryId>>,
  output: OutputCallback,
}

pub enum Until {
  Timestamp(Timestamp),
  Eternity,
}

impl<EventType: Copy, OutputCallback: FnMut(OutEvent)>
Controller<EventType, OutputCallback> {
  fn new(output: OutputCallback) -> Self {
    Self {
      simtime: 0,
      next_id: 0,
      queue: BinaryHeap::with_capacity(8),
      removed: BinaryHeap::with_capacity(4),
      output,
    }
  }
  fn set_timeout(&mut self, delay: Timestamp, event: EventType) -> EntryId {
    let id = EntryId{ timestamp: self.simtime + delay, n: self.next_id };
    let entry = QueueEntry::<EventType>{ id, event };
    self.queue.push(Reverse(entry));
    self.next_id += 1; // TODO: will overflow eventually :(
    return id
  }
  fn unset_timeout(&mut self, id: EntryId) {
    self.removed.push(Reverse(id));
  }
  fn run_until<StatechartType: SC<EventType, Controller<EventType, OutputCallback>>>(&mut self, sc: &mut StatechartType, until: Until) {
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
        println!("time is now {}", self.simtime);
        sc.big_step(Some(entry.event), self);
        self.queue.pop();
      }
      else {
        break 'running;
      }
    }
  }
}
