// Helpers and traits implemented by, or used by from-statechart-generated Rust code.

pub trait EventLifeline<T> {
  fn current(&self) -> &T;
  fn raise(&mut self) -> &mut T;
  fn cycle(&mut self);
}

#[derive(Default)]
pub struct SameRoundLifeline<T> {
  current: T,
}

impl<T: Default> EventLifeline<T> for SameRoundLifeline<T> {
  fn current(&self) -> &T {
    &self.current
  }
  fn raise(&mut self) -> &mut T {
    &mut self.current
  }
  fn cycle(&mut self) {
    // Reset
    self.current = Default::default()
  }
}

enum Which {
  One,
  Two,
}
impl Default for Which {
  fn default() -> Self {
    Self::One
  }
}

#[derive(Default)]
pub struct NextRoundLifeline<T> {
  one: T,
  two: T,

  current: Which,
}

impl<T: Default> EventLifeline<T> for NextRoundLifeline<T> {
  fn current(&self) -> &T {
    match self.current {
      Which::One => &self.one,
      Which::Two => &self.two,
    }
  }
  fn raise(&mut self) -> &mut T {
    match self.current {
      // Raise in the next round
      Which::One => &mut self.two,
      Which::Two => &mut self.one,
    }
  }
  fn cycle(&mut self) {
    match self.current {
      Which::One => {
        self.one = Default::default();
        self.current = Which::Two;
      },
      Which::Two => {
        self.two = Default::default();
        self.current = Which::One;
      },
    };
  }
}

// For simplicity, we assume timestamps are always 32-bit unsigned integers.
// This type is large enough for practical purposes, and has better performance than 64-bit unsigned integers, even on amd64 architectures.
pub type Timestamp = u32;

// This trait defines the scheduler-operations a statechart may call during a step.
// By defining them in a trait, the generated statechart code can be independent of the
// scheduler (event queue) implementation.
pub trait Scheduler<InEvent, TimerId> {
  fn set_timeout(&mut self, delay: Timestamp, event: InEvent) -> TimerId;
  fn unset_timeout(&mut self, id: TimerId);
}

// Generated statechart types will implement this trait.
pub trait SC<InEvent, TimerId, Sched: Scheduler<InEvent, TimerId>, OutputCallback> {
  fn init(&mut self, sched: &mut Sched, output: &mut OutputCallback);
  fn big_step(&mut self, event: Option<InEvent>, sched: &mut Sched, output: &mut OutputCallback);
}
