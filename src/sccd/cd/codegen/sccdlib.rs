use std::collections::BinaryHeap;
use std::collections::binary_heap::PeekMut;
use std::cmp::Ordering;

type Timestamp = usize; // unsigned integer, platform's word size
// type OutputCallback = fn(&str, &str);

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

pub enum Target<'a, EventType, OutputCallback> {
  Narrowcast(&'a mut dyn SC<EventType, OutputCallback>),
  Broadcast,
}

pub struct Entry<'a, EventType, OutputCallback> {
  timestamp: Timestamp,
  event: EventType,
  target: Target<'a, EventType, OutputCallback>,
}

impl<'a, EventType, OutputCallback> Ord for Entry<'a, EventType, OutputCallback> {
  fn cmp(&self, other: &Self) -> Ordering {
    self.timestamp.cmp(&other.timestamp).reverse()
  }
}

impl<'a, EventType, OutputCallback> PartialOrd for Entry<'a, EventType, OutputCallback> {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl<'a, EventType, OutputCallback> PartialEq for Entry<'a, EventType, OutputCallback> {
    fn eq(&self, other: &Self) -> bool {
        self.timestamp == other.timestamp
    }
}

impl<'a, EventType, OutputCallback> Eq for Entry<'a, EventType, OutputCallback> {}


pub struct Controller<'a, EventType, OutputCallback> {
  queue: BinaryHeap<Entry<'a, EventType, OutputCallback>>,
  simtime: Timestamp,
  output: OutputCallback,
}

// impl<'a, EventType> Default for Controller<'a, EventType> {
//   fn default() -> Self {
//     Self {
//       queue: BinaryHeap::new(),
//       simtime: 0,
//     }
//   }
// }

pub enum Until {
  Timestamp(Timestamp),
  Eternity,
}

impl<'a, EventType: Copy, OutputCallback: FnMut(&'static str, &'static str)> Controller<'a, EventType, OutputCallback> {
  fn new(output: OutputCallback) -> Self {
    Self {
      queue: BinaryHeap::new(),
      simtime: 0,
      output,
    }
  }
  fn add_input(&mut self, entry: Entry<'a, EventType, OutputCallback>) {
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

          match &mut entry.target {
            Target::Narrowcast(sc) => {
              sc.fair_step(Some(e), &mut self.output);
            },
            Target::Broadcast => {
              println!("broadcast not implemented!")
            },
          };

          PeekMut::<'_, Entry<'a, EventType, OutputCallback>>::pop(entry);
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
