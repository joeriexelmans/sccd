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
pub fn add_event(h: &mut Handle, delay: statechart::Timestamp, i: digitalwatch::InEvent) {
  h.controller.set_timeout(delay, i);
}

// Wasm_bindgen cannot yet create bindings for enums with values (such as controller::Until) or tuples, so we translate it to a simple struct
#[wasm_bindgen]
pub struct RunUntilResult {
  pub simtime: statechart::Timestamp,
  pub next_wakeup_eternity: bool,
  pub next_wakeup: statechart::Timestamp,
}

impl RunUntilResult {
  fn new(simtime: statechart::Timestamp, next_wakeup: controller::Until) -> Self {
    match next_wakeup {
      controller::Until::Timestamp(t) => Self{
        simtime,
        next_wakeup_eternity: false,
        next_wakeup: t,
      },
      controller::Until::Eternity => Self{
        simtime,
        next_wakeup_eternity: true,
        next_wakeup: 0,
      },
    }
  }
}

#[wasm_bindgen]
pub fn run_until(h: &mut Handle, t: statechart::Timestamp, out: &OutputHandler) -> RunUntilResult {
  let (simtime, next_wakeup) = h.controller.run_until(&mut h.statechart, controller::Until::Timestamp(t), &mut |e|{ out.handle_output(e) });

  RunUntilResult::new(simtime, next_wakeup)
}
