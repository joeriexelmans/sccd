use wasm_bindgen::prelude::*;

use sccd::controller;
use sccd::statechart;

// Traits
use sccd::statechart::SC;
use sccd::statechart::Scheduler;


#[wasm_bindgen]
extern "C" {
  #[wasm_bindgen(js_namespace = console)]
  fn log(s: &str);
}

#[wasm_bindgen(module = "/outputhandler.js")]
extern "C" {
  pub type OutputHandler;

  #[wasm_bindgen(method)]
  fn handle_output(this: &OutputHandler, e: digitalwatch::OutEvent);
}


#[wasm_bindgen]
extern {
  fn alert(s: &str);
}

#[wasm_bindgen]
#[derive(Default)]
pub struct Handle {
  controller: controller::Controller<digitalwatch::InEvent>,
  statechart: digitalwatch::Statechart<controller::Controller<digitalwatch::InEvent>>,
}

#[wasm_bindgen]
pub fn setup(out: &OutputHandler) -> Handle {
  let mut handle = Handle::default();
  handle.statechart.init(&mut handle.controller, &mut |e|{ out.handle_output(e) });

  handle
}

#[wasm_bindgen]
pub fn add_event(h: &mut Handle, delay: statechart::Timestamp, i: digitalwatch::InEvent) -> RunUntilResult {
  h.controller.set_timeout(delay, i);
  RunUntilResult::from_controller(&h.controller)
}

#[wasm_bindgen]
pub struct RunUntilResult {
  pub simtime: statechart::Timestamp,
  pub reschedule: bool,
  pub at: statechart::Timestamp,
}

impl RunUntilResult {
  fn from_controller(c: &controller::Controller::<digitalwatch::InEvent>) -> Self {
    let mut result = match c.get_earliest() {
      controller::Until::Timestamp(t) => RunUntilResult{reschedule: true, at: t, simtime: 0},
      controller::Until::Eternity => RunUntilResult{reschedule: false, at: 0, simtime: 0},
    };
    result.simtime = c.get_simtime();
    result
  }
}

#[wasm_bindgen]
pub fn run_until(h: &mut Handle, t: statechart::Timestamp, out: &OutputHandler) -> RunUntilResult {
  h.controller.run_until(&mut h.statechart, controller::Until::Timestamp(t), &mut |e|{ out.handle_output(e) });
  RunUntilResult::from_controller(&h.controller)
}
