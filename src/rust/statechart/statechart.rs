mod sccd {
  // Helpers and traits implemented by, or used by from-statechart-generated Rust code.
  mod statechart {

    pub trait EventLifeline<T> {
      fn get(&self) -> &T;
      fn get_mut(&mut self) -> &mut T;
      fn cycle(&mut self);
    }

    #[derive(Default)]
    pub struct SameRoundLifeline<T> {
      current: T,
    }

    impl<T: Default> EventLifeline<T> for SameRoundLifeline<T> {
      fn get(&self) -> &T {
        &self.current
      }
      fn get_mut(&mut self) -> &mut T {
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
      fn get(&self) -> &T {
        match self.current {
          Which::One => &self.one,
          Which::Two => &self.two,
        }
      }
      fn get_mut(&mut self) -> &mut T {
        match self.current {
          Which::One => &mut self.one,
          Which::Two => &mut self.two,
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

    pub type Timestamp = u32;

    pub trait Scheduler<InEvent, EntryId> {
      fn set_timeout(&mut self, delay: Timestamp, event: InEvent) -> EntryId;
      fn unset_timeout(&mut self, id: EntryId);
    }

    pub trait SC<InEvent, EntryId, Sched: Scheduler<InEvent, EntryId>, OutputCallback> {
      fn init(&mut self, sched: &mut Sched, output: &mut OutputCallback);
      fn big_step(&mut self, event: Option<InEvent>, sched: &mut Sched, output: &mut OutputCallback);
    }

    // TODO: Does not belong in "common", this should become a statechart-specific enum-type.
    #[derive(Debug, Eq, PartialEq)]
    pub struct OutEvent {
      port: &'static str,
      event: &'static str,
    }
  }
}
