use std::collections::BinaryHeap;
use std::collections::binary_heap::PeekMut;
use std::cmp::Ordering;

type Timestamp = usize; // unsigned integer, platform's word size

pub trait State<OutputCallback> {
  fn enter_actions(output: &mut OutputCallback);
  fn exit_actions(output: &mut OutputCallback);
  fn enter_default(output: &mut OutputCallback);

  fn exit_current(&self, output: &mut OutputCallback);
}

pub trait SC<EventType, OutputCallback> {
  fn init(&self, output: &mut OutputCallback);
  fn fair_step(&mut self, event: Option<EventType>, output: &mut OutputCallback);
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

impl<'a, EventType: Copy, OutputCallback: FnMut(&'a str, &'a str), StatechartType: SC<EventType, OutputCallback>>
Controller<EventType, OutputCallback, StatechartType> {
  fn new(statechart: StatechartType, output: OutputCallback) -> Self {
    Self {
      statechart,
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
        Some(mut entry) => {
          if let Until::Timestamp(t) = until {
            if entry.timestamp > t {
              println!("break, timestamp {}, t {}", entry.timestamp, t);
              break 'running;
            }
          }

          self.simtime = entry.timestamp;
          println!("time is now {}", self.simtime);

          let e = entry.event; // copy

          self.statechart.fair_step(Some(e), &mut self.output);

          PeekMut::<'_, Entry<EventType>>::pop(entry);
        },
        None => { break 'running; },
      }
    }
  }
}



/// TEST CODE

// #[derive(Copy, Clone)]
// enum Event {
//   A,
//   B,
// }

// fn main() {
//   let mut c: Controller<Event> = Default::default();
//   c.add_input(Entry::<Event>{
//     timestamp: 3,
//     event: Event::A,
//     target: Target::Broadcast,
//   });
//   c.add_input(Entry::<Event>{
//     timestamp: 1,
//     event: Event::A,
//     target: Target::Broadcast,
//   });
//   c.add_input(Entry::<Event>{
//     timestamp: 30,
//     event: Event::A,
//     target: Target::Broadcast,
//   });
//   c.add_input(Entry::<Event>{
//     timestamp: 5,
//     event: Event::A,
//     target: Target::Broadcast,
//   });
//   c.run_until(Until::Timestamp(10));
// }
