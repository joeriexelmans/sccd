use std::collections::BinaryHeap;
use std::collections::binary_heap::PeekMut;
use std::cmp::Ordering;

type Timestamp = usize; // unsigned integer, platform's word size

pub trait State<OutputCallback> {
  // Execute enter actions of only this state
  fn enter_actions(output: &mut OutputCallback);
  // Execute exit actions of only this state
  fn exit_actions(output: &mut OutputCallback);
  // Execute enter actions of this state and its 'default' child(ren), recursively
  fn enter_default(output: &mut OutputCallback);

  // Execute enter actions as if the configuration recorded in this state is being entered
  fn enter_current(&self, output: &mut OutputCallback);
  // Execute exit actions as if the configuration recorded in this state is being exited
  fn exit_current(&self, output: &mut OutputCallback);
}

pub trait SC<EventType, OutputCallback> {
  fn init(output: &mut OutputCallback);
  fn big_step(&mut self, event: Option<EventType>, output: &mut OutputCallback);
}

pub struct Entry<EventType> {
  timestamp: Timestamp,
  event: EventType,
}

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


pub struct Controller<EventType, OutputCallback, StatechartType: SC<EventType, OutputCallback>> {
  statechart: StatechartType,
  output: OutputCallback,
  queue: BinaryHeap<Entry<EventType>>,
  simtime: Timestamp,
}

pub enum Until {
  Timestamp(Timestamp),
  Eternity,
}

impl<'a, EventType: Copy, OutputCallback: FnMut(&'a str, &'a str), StatechartType: SC<EventType, OutputCallback> + Default>
Controller<EventType, OutputCallback, StatechartType> {
  fn new(output: OutputCallback) -> Self {
    Self {
      statechart: Default::default(),
      output,
      queue: BinaryHeap::new(),
      simtime: 0,
    }
  }
  fn add_input(&mut self, entry: Entry<EventType>) {
    self.queue.push(entry);
  }
  fn run_until(&mut self, until: Until) {
    'running: loop {
      match self.queue.peek_mut() {
        Some(entry) => {
          if let Until::Timestamp(t) = until {
            if entry.timestamp > t {
              println!("break, timestamp {}, t {}", entry.timestamp, t);
              break 'running;
            }
          }

          self.simtime = entry.timestamp;
          println!("time is now {}", self.simtime);

          let e = entry.event; // copy

          self.statechart.big_step(Some(e), &mut self.output);

          PeekMut::pop(entry);
        },
        None => { break 'running; },
      }
    }
  }
}
