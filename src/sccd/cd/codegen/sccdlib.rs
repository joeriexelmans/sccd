use std::collections::BinaryHeap;
use std::collections::binary_heap::PeekMut;
use std::cmp::Ordering;

type Timestamp = usize; // unsigned integer, platform's word size
type OutputCallback = fn(&str, &str);

pub trait State {
  fn enter_actions(output: OutputCallback);
  fn exit_actions(output: OutputCallback);
  fn enter_default(output: OutputCallback);

  fn exit_current(&self, output: OutputCallback);
}

pub trait SC<EventType> {
  fn init(&self, output: OutputCallback);
  fn fair_step(&mut self, event: Option<EventType>, output: OutputCallback);
}

pub enum Target<'a, EventType> {
  Narrowcast(&'a mut dyn SC<EventType>),
  Broadcast,
}

pub struct Entry<'a, EventType> {
  timestamp: Timestamp,
  event: EventType,
  target: Target<'a, EventType>,
}

impl<'a, EventType> Ord for Entry<'a, EventType> {
  fn cmp(&self, other: &Self) -> Ordering {
    self.timestamp.cmp(&other.timestamp).reverse()
  }
}

impl<'a, EventType> PartialOrd for Entry<'a, EventType> {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl<'a, EventType> PartialEq for Entry<'a, EventType> {
    fn eq(&self, other: &Self) -> bool {
        self.timestamp == other.timestamp
    }
}

impl<'a, EventType> Eq for Entry<'a, EventType> {}


pub struct Controller<'a, EventType> {
  queue: BinaryHeap<Entry<'a, EventType>>,
  simtime: Timestamp,
  output_callback: fn(&str, &str),
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

impl<'a, EventType: Copy> Controller<'a, EventType> {
  fn new(output_callback: fn(&str, &str)) -> Self {
    Self {
      queue: BinaryHeap::new(),
      simtime: 0,
      output_callback,
    }
  }
  fn add_input(&mut self, entry: Entry<'a, EventType>) {
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
              sc.fair_step(Some(e), self.output_callback);
            },
            Target::Broadcast => {
              println!("broadcast not implemented!")
            },
          };

          PeekMut::<'_, Entry<'a, EventType>>::pop(entry);
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
