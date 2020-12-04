use std::collections::BinaryHeap;
use std::cmp::Ordering;

type Timestamp = usize;

type TimerId = usize;

pub trait State<TimersType, Handle> {
  // Execute enter actions of only this state
  fn enter_actions(timers: &mut TimersType, handle: &mut Handle);
  // Execute exit actions of only this state
  fn exit_actions(timers: &mut TimersType, handle: &mut Handle);

  // Execute enter actions of this state and its 'default' child(ren), recursively
  fn enter_default(timers: &mut TimersType, handle: &mut Handle);

  // Execute enter actions as if the configuration recorded in this state is being entered
  fn enter_current(&self, timers: &mut TimersType, handle: &mut Handle);
  // Execute exit actions as if the configuration recorded in this state is being exited
  fn exit_current(&self, timers: &mut TimersType, handle: &mut Handle);
}

pub trait SC<EventType, Handle> {
  fn init(&mut self, handle: &mut Handle);
  fn big_step(&mut self, event: Option<EventType>, handle: &mut Handle);
}

pub struct Entry<EventType> {
  timestamp: Timestamp,
  event: EventType,
  id: TimerId,
}

// impl<EventType> Entry<EventType> {
//   fn new(timestamp: Timestamp, event: EventType) -> Entry<EventType> {
//     Self{ timestamp, event, removed: false }
//   }
// }

// In order to implement Ord, also gotta implement PartialOrd, PartialEq and Eq:

impl<EventType> Ord for Entry<EventType> {
  fn cmp(&self, other: &Self) -> Ordering {
    self.timestamp.cmp(&other.timestamp).reverse()
  }
}
impl<EventType> PartialOrd for Entry<EventType> {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}
impl<EventType> PartialEq for Entry<EventType> {
    fn eq(&self, other: &Self) -> bool {
        self.timestamp == other.timestamp
    }
}
impl<EventType> Eq for Entry<EventType> {}

pub struct Handle<EventType, OutputCallback> {
  simtime: Timestamp,
  next_id: TimerId,
  queue: BinaryHeap<Entry<EventType>>,
  removed: BinaryHeap<TimerId>,
  output: OutputCallback,
}

impl<EventType, OutputCallback> Handle<EventType, OutputCallback> {
  fn set_timeout(&mut self, delay: Timestamp, event: EventType) -> TimerId {
    let id = self.next_id;
    let entry = Entry::<EventType>{ timestamp: self.simtime + delay, event, id };
    self.queue.push(entry);
    self.next_id = self.next_id.wrapping_add(1); // increment with overflow
    return id
  }
  fn unset_timeout(&mut self, id: TimerId) {
    self.removed.push(id);
  }
}

pub struct Controller<EventType, OutputCallback, StatechartType: SC<EventType, Handle<EventType, OutputCallback>>> {
  handle: Handle<EventType, OutputCallback>,
  statechart: StatechartType,
}

pub enum Until {
  Timestamp(Timestamp),
  Eternity,
}

impl<'a, EventType: Copy, OutputCallback: FnMut(&'a str, &'a str), StatechartType: SC<EventType, Handle<EventType, OutputCallback>> + Default>
Controller<EventType, OutputCallback, StatechartType> {
  fn new(output: OutputCallback) -> Self {
    Self {
      statechart: Default::default(),
      handle: Handle {
        simtime: 0,
        next_id: 0,
        queue: BinaryHeap::new(),
        removed: BinaryHeap::new(),
        output,
      },
    }
  }
  fn add_input(&mut self, event: EventType) {
    self.handle.set_timeout(0, event);
    // self.handle.queue.push(entry);
  }
  fn run_until(&mut self, until: Until) {
    'running: loop {
      if let Some(entry) = self.handle.queue.peek() {
        // Check if event was removed
        if let Some(removed) = self.handle.removed.peek() {
          if entry.id == *removed {
            self.handle.queue.pop();
            self.handle.removed.pop();
            continue;
          }
        }
        // Check if event too far in the future
        if let Until::Timestamp(t) = until {
          if entry.timestamp > t {
            println!("break, timestamp {}, t {}", entry.timestamp, t);
            break 'running;
          }
        }
        // OK, handle event
        self.handle.simtime = entry.timestamp;
        println!("time is now {}", self.handle.simtime);
        self.statechart.big_step(Some(entry.event), &mut self.handle);
        self.handle.queue.pop();
      }
      else {
        break 'running;
      }
    }
  }
}
