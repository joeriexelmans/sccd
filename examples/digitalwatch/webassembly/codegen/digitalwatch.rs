#![allow(non_camel_case_types)]
#![allow(non_snake_case)]
#![allow(unused_labels)]
#![allow(unused_variables)]
#![allow(dead_code)]
#![allow(unused_parens)]
#![allow(unused_macros)]
#![allow(non_upper_case_globals)]
#![allow(unused_mut)]
#![allow(unused_imports)]

#[cfg(target_arch = "wasm32")]
use wasm_bindgen::prelude::*;

use std::ops::Deref;
use std::ops::DerefMut;

use sccd::action_lang;
use sccd::inherit_struct;
use sccd::call_closure;
use sccd::statechart;
use sccd::statechart::EventLifeline;

type Timers<TimerId> = [TimerId; 11];

// Input Events
#[cfg_attr(target_arch = "wasm32", wasm_bindgen)]
#[derive(Copy, Clone, Debug)]
pub enum InEvent {
  E_bottomLeftPressed,
  E_bottomLeftReleased,
  E_bottomRightPressed,
  E_bottomRightReleased,
  E_topLeftPressed,
  E_topLeftReleased,
  E_topRightPressed,
  E_topRightReleased,
  E_alarmStart,
  A0,
  A1,
  A2,
  A3,
  A4,
  A5,
  A6,
  A7,
  A8,
  A9,
  A10,
}

// Internal Events
struct Event_int_refresh_chrono {
  // TODO: internal event parameters
}
struct Event_int_refresh_time {
  // TODO: internal event parameters
}
struct Event_alarm_edit {
  // TODO: internal event parameters
}
struct Event_time_edit {
  // TODO: internal event parameters
}
struct Event_edit_done {
  // TODO: internal event parameters
}
#[derive(Default)]
struct Internal {
  e_int_refresh_chrono: Option<Event_int_refresh_chrono>,
  e_int_refresh_time: Option<Event_int_refresh_time>,
  e_alarm_edit: Option<Event_alarm_edit>,
  e_time_edit: Option<Event_time_edit>,
  e_edit_done: Option<Event_edit_done>,
}
type InternalLifeline = statechart::NextRoundLifeline<Internal>;

// Output Events
#[cfg_attr(target_arch = "wasm32", wasm_bindgen)]
#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub enum OutEvent {
  E_setAlarm,
  E_setIndiglo,
  E_unsetIndiglo,
  E_increaseChronoByOne,
  E_resetChrono,
  E_refreshTimeDisplay,
  E_refreshAlarmDisplay,
  E_startSelection,
  E_stopSelection,
  E_selectNext,
  E_increaseSelection,
  E_refreshChronoDisplay,
  E_increaseTimeByOne,
  E_checkTime,
}

// Transition arenas (bitmap type)
type Arenas = u16;
const ARENA_NONE: Arenas = 0;
const ARENA_P_Alarm: Arenas = 0b111;
const ARENA_P_Alarm_On: Arenas = 0b110;
const ARENA_P_Alarm_On_Blinking: Arenas = 0b100;
const ARENA_P_Indiglo: Arenas = 0b1000;
const ARENA_P_ChronoWrapper: Arenas = 0b110000;
const ARENA_P_ChronoWrapper_Chrono: Arenas = 0b100000;
const ARENA_P_Display: Arenas = 0b11000000;
const ARENA_P_Display_EditingTime: Arenas = 0b10000000;
const ARENA_P_Time: Arenas = 0b100000000;
const ARENA_UNSTABLE: Arenas = 0b1000000000; // indicates any transition fired with an unstable target

impl<Sched: statechart::Scheduler> Default for Statechart<Sched> {
  fn default() -> Self {
    // Initialize data model
    let scope = action_lang::Empty{};
    Self {
      configuration: Default::default(),
      timers: Default::default(),
      data: scope,
    }
  }
}
type DataModel = action_lang::Empty;
pub struct Statechart<Sched: statechart::Scheduler> {
  configuration: Root,
  timers: Timers<Sched::TimerId>,
  data: DataModel,
}

fn fair_step<Sched: statechart::Scheduler<InEvent=InEvent>>(sc: &mut Statechart<Sched>, input: &mut Option<InEvent>, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent), dirty: Arenas) -> Arenas {
  let mut fired: Arenas = ARENA_NONE;
  let mut scope = &mut sc.data;
  let root = &mut sc.configuration;
  'arena_root: loop {
    match *root {
      Root::S_P(ref mut s_P) => {
        let s_P_Alarm = &mut s_P.s_P_Alarm;
        let s_P_Indiglo = &mut s_P.s_P_Indiglo;
        let s_P_ChronoWrapper = &mut s_P.s_P_ChronoWrapper;
        let s_P_Display = &mut s_P.s_P_Display;
        let s_P_Time = &mut s_P.s_P_Time;
        // Orthogonal region
        if (fired | dirty) & ARENA_P_Alarm == ARENA_NONE {
          'arena_P_Alarm: loop {
            match *s_P_Alarm {
              State_P_Alarm::S_Off(ref mut s_P_Alarm_Off) => {
                // Outgoing transition 0
                if let Some(InEvent::E_bottomLeftPressed) = &input {
                  if f0_guard((*s_P_Indiglo, *s_P_ChronoWrapper, *s_P_Display, *s_P_Time, ), ) {
                    // Exit actions
                    s_P_Alarm_Off.exit_current(&mut sc.timers, scope, internal, sched, output);
                    // Enter actions
                    State_P_Alarm_On::enter_default(&mut sc.timers, scope, internal, sched, output);
                    // Build new state configuration
                    let new_s_P_Alarm_On: State_P_Alarm_On = Default::default();
                    let new_s_P_Alarm = State_P_Alarm::S_On(new_s_P_Alarm_On);
                    // Update arena configuration
                    *s_P_Alarm = new_s_P_Alarm;
                    fired |= ARENA_P_Alarm; // Stable target
                    // Internal Event Lifeline: Next Small Step
                    internal.cycle();
                    break 'arena_P_Alarm;
                  }
                }
              },
              State_P_Alarm::S_On(ref mut s_P_Alarm_On) => {
                if (fired | dirty) & ARENA_P_Alarm_On == ARENA_NONE {
                  'arena_P_Alarm_On: loop {
                    match *s_P_Alarm_On {
                      State_P_Alarm_On::S_NotBlinking(ref mut s_P_Alarm_On_NotBlinking) => {
                        // Outgoing transition 0
                        if let Some(InEvent::E_alarmStart) = &input {
                          // Exit actions
                          s_P_Alarm_On_NotBlinking.exit_current(&mut sc.timers, scope, internal, sched, output);
                          // Enter actions
                          State_P_Alarm_On_Blinking::enter_default(&mut sc.timers, scope, internal, sched, output);
                          // Build new state configuration
                          let new_s_P_Alarm_On_Blinking: State_P_Alarm_On_Blinking = Default::default();
                          let new_s_P_Alarm_On = State_P_Alarm_On::S_Blinking(new_s_P_Alarm_On_Blinking);
                          // Update arena configuration
                          *s_P_Alarm_On = new_s_P_Alarm_On;
                          fired |= ARENA_P_Alarm_On; // Stable target
                          // Internal Event Lifeline: Next Small Step
                          internal.cycle();
                          break 'arena_P_Alarm_On;
                        }
                        // Outgoing transition 1
                        // A transition may have fired earlier that overlaps with our arena:
                        if fired & (ARENA_P_Alarm) == ARENA_NONE {
                          if let Some(InEvent::E_bottomLeftPressed) = &input {
                            if f1_guard((*s_P_Indiglo, *s_P_ChronoWrapper, *s_P_Display, *s_P_Time, ), ) {
                              // Exit actions
                              s_P_Alarm_On_NotBlinking.exit_current(&mut sc.timers, scope, internal, sched, output);
                              State_P_Alarm_On::exit_actions(&mut sc.timers, scope, internal, sched, output);
                              // Enter actions
                              State_P_Alarm_Off::enter_default(&mut sc.timers, scope, internal, sched, output);
                              // Build new state configuration
                              let new_s_P_Alarm_Off: State_P_Alarm_Off = Default::default();
                              let new_s_P_Alarm = State_P_Alarm::S_Off(new_s_P_Alarm_Off);
                              // Update arena configuration
                              *s_P_Alarm = new_s_P_Alarm;
                              fired |= ARENA_P_Alarm; // Stable target
                              // Internal Event Lifeline: Next Small Step
                              internal.cycle();
                              break 'arena_P_Alarm;
                            }
                          }
                        }
                      },
                      State_P_Alarm_On::S_Blinking(ref mut s_P_Alarm_On_Blinking) => {
                        // Outgoing transition 0
                        // A transition may have fired earlier that overlaps with our arena:
                        if fired & (ARENA_P_Alarm) == ARENA_NONE {
                          if let Some(InEvent::E_topRightPressed) = &input {
                            // Exit actions
                            s_P_Alarm_On_Blinking.exit_current(&mut sc.timers, scope, internal, sched, output);
                            State_P_Alarm_On::exit_actions(&mut sc.timers, scope, internal, sched, output);
                            // Enter actions
                            State_P_Alarm_Off::enter_default(&mut sc.timers, scope, internal, sched, output);
                            // Build new state configuration
                            let new_s_P_Alarm_Off: State_P_Alarm_Off = Default::default();
                            let new_s_P_Alarm = State_P_Alarm::S_Off(new_s_P_Alarm_Off);
                            // Update arena configuration
                            *s_P_Alarm = new_s_P_Alarm;
                            fired |= ARENA_P_Alarm; // Stable target
                            // Internal Event Lifeline: Next Small Step
                            internal.cycle();
                            break 'arena_P_Alarm;
                          }
                        }
                        // Outgoing transition 1
                        // A transition may have fired earlier that overlaps with our arena:
                        if fired & (ARENA_P_Alarm) == ARENA_NONE {
                          if let Some(InEvent::E_topLeftPressed) = &input {
                            // Exit actions
                            s_P_Alarm_On_Blinking.exit_current(&mut sc.timers, scope, internal, sched, output);
                            State_P_Alarm_On::exit_actions(&mut sc.timers, scope, internal, sched, output);
                            // Enter actions
                            State_P_Alarm_Off::enter_default(&mut sc.timers, scope, internal, sched, output);
                            // Build new state configuration
                            let new_s_P_Alarm_Off: State_P_Alarm_Off = Default::default();
                            let new_s_P_Alarm = State_P_Alarm::S_Off(new_s_P_Alarm_Off);
                            // Update arena configuration
                            *s_P_Alarm = new_s_P_Alarm;
                            fired |= ARENA_P_Alarm; // Stable target
                            // Internal Event Lifeline: Next Small Step
                            internal.cycle();
                            break 'arena_P_Alarm;
                          }
                        }
                        // Outgoing transition 2
                        // A transition may have fired earlier that overlaps with our arena:
                        if fired & (ARENA_P_Alarm) == ARENA_NONE {
                          if let Some(InEvent::E_bottomRightPressed) = &input {
                            // Exit actions
                            s_P_Alarm_On_Blinking.exit_current(&mut sc.timers, scope, internal, sched, output);
                            State_P_Alarm_On::exit_actions(&mut sc.timers, scope, internal, sched, output);
                            // Enter actions
                            State_P_Alarm_Off::enter_default(&mut sc.timers, scope, internal, sched, output);
                            // Build new state configuration
                            let new_s_P_Alarm_Off: State_P_Alarm_Off = Default::default();
                            let new_s_P_Alarm = State_P_Alarm::S_Off(new_s_P_Alarm_Off);
                            // Update arena configuration
                            *s_P_Alarm = new_s_P_Alarm;
                            fired |= ARENA_P_Alarm; // Stable target
                            // Internal Event Lifeline: Next Small Step
                            internal.cycle();
                            break 'arena_P_Alarm;
                          }
                        }
                        // Outgoing transition 3
                        // A transition may have fired earlier that overlaps with our arena:
                        if fired & (ARENA_P_Alarm) == ARENA_NONE {
                          if let Some(InEvent::E_bottomLeftPressed) = &input {
                            // Exit actions
                            s_P_Alarm_On_Blinking.exit_current(&mut sc.timers, scope, internal, sched, output);
                            State_P_Alarm_On::exit_actions(&mut sc.timers, scope, internal, sched, output);
                            // Enter actions
                            State_P_Alarm_Off::enter_default(&mut sc.timers, scope, internal, sched, output);
                            // Build new state configuration
                            let new_s_P_Alarm_Off: State_P_Alarm_Off = Default::default();
                            let new_s_P_Alarm = State_P_Alarm::S_Off(new_s_P_Alarm_Off);
                            // Update arena configuration
                            *s_P_Alarm = new_s_P_Alarm;
                            fired |= ARENA_P_Alarm; // Stable target
                            // Internal Event Lifeline: Next Small Step
                            internal.cycle();
                            break 'arena_P_Alarm;
                          }
                        }
                        // Outgoing transition 4
                        // A transition may have fired earlier that overlaps with our arena:
                        if fired & (ARENA_P_Alarm_On) == ARENA_NONE {
                          if let Some(InEvent::A2) = &input {
                            // Exit actions
                            s_P_Alarm_On_Blinking.exit_current(&mut sc.timers, scope, internal, sched, output);
                            // Enter actions
                            State_P_Alarm_On_NotBlinking::enter_default(&mut sc.timers, scope, internal, sched, output);
                            // Build new state configuration
                            let new_s_P_Alarm_On_NotBlinking: State_P_Alarm_On_NotBlinking = Default::default();
                            let new_s_P_Alarm_On = State_P_Alarm_On::S_NotBlinking(new_s_P_Alarm_On_NotBlinking);
                            // Update arena configuration
                            *s_P_Alarm_On = new_s_P_Alarm_On;
                            fired |= ARENA_P_Alarm_On; // Stable target
                            // Internal Event Lifeline: Next Small Step
                            internal.cycle();
                            break 'arena_P_Alarm_On;
                          }
                        }
                        if (fired | dirty) & ARENA_P_Alarm_On_Blinking == ARENA_NONE {
                          'arena_P_Alarm_On_Blinking: loop {
                            match *s_P_Alarm_On_Blinking {
                              State_P_Alarm_On_Blinking::S_On(ref mut s_P_Alarm_On_Blinking_On) => {
                                // Outgoing transition 0
                                if let Some(InEvent::A0) = &input {
                                  // Exit actions
                                  s_P_Alarm_On_Blinking_On.exit_current(&mut sc.timers, scope, internal, sched, output);
                                  // Enter actions
                                  State_P_Alarm_On_Blinking_Off::enter_default(&mut sc.timers, scope, internal, sched, output);
                                  // Build new state configuration
                                  let new_s_P_Alarm_On_Blinking_Off: State_P_Alarm_On_Blinking_Off = Default::default();
                                  let new_s_P_Alarm_On_Blinking = State_P_Alarm_On_Blinking::S_Off(new_s_P_Alarm_On_Blinking_Off);
                                  // Update arena configuration
                                  *s_P_Alarm_On_Blinking = new_s_P_Alarm_On_Blinking;
                                  fired |= ARENA_P_Alarm_On_Blinking; // Stable target
                                  // Internal Event Lifeline: Next Small Step
                                  internal.cycle();
                                  break 'arena_P_Alarm_On_Blinking;
                                }
                              },
                              State_P_Alarm_On_Blinking::S_Off(ref mut s_P_Alarm_On_Blinking_Off) => {
                                // Outgoing transition 0
                                // A transition may have fired earlier that overlaps with our arena:
                                if fired & (ARENA_P_Alarm_On_Blinking) == ARENA_NONE {
                                  if let Some(InEvent::A1) = &input {
                                    // Exit actions
                                    s_P_Alarm_On_Blinking_Off.exit_current(&mut sc.timers, scope, internal, sched, output);
                                    // Enter actions
                                    State_P_Alarm_On_Blinking_On::enter_default(&mut sc.timers, scope, internal, sched, output);
                                    // Build new state configuration
                                    let new_s_P_Alarm_On_Blinking_On: State_P_Alarm_On_Blinking_On = Default::default();
                                    let new_s_P_Alarm_On_Blinking = State_P_Alarm_On_Blinking::S_On(new_s_P_Alarm_On_Blinking_On);
                                    // Update arena configuration
                                    *s_P_Alarm_On_Blinking = new_s_P_Alarm_On_Blinking;
                                    fired |= ARENA_P_Alarm_On_Blinking; // Stable target
                                    // Internal Event Lifeline: Next Small Step
                                    internal.cycle();
                                    break 'arena_P_Alarm_On_Blinking;
                                  }
                                }
                              },
                            };
                            break;
                          }
                        }
                      },
                    };
                    break;
                  }
                }
              },
            };
            break;
          }
        }
        // Orthogonal region
        if (fired | dirty) & ARENA_P_Indiglo == ARENA_NONE {
          'arena_P_Indiglo: loop {
            match *s_P_Indiglo {
              State_P_Indiglo::S_Off(ref mut s_P_Indiglo_Off) => {
                // Outgoing transition 0
                if let Some(InEvent::E_topRightPressed) = &input {
                  // Exit actions
                  s_P_Indiglo_Off.exit_current(&mut sc.timers, scope, internal, sched, output);
                  // Transition's actions
                  (output)(OutEvent::E_setIndiglo);
                  // Enter actions
                  State_P_Indiglo_Pushed::enter_default(&mut sc.timers, scope, internal, sched, output);
                  // Build new state configuration
                  let new_s_P_Indiglo_Pushed: State_P_Indiglo_Pushed = Default::default();
                  let new_s_P_Indiglo = State_P_Indiglo::S_Pushed(new_s_P_Indiglo_Pushed);
                  // Update arena configuration
                  *s_P_Indiglo = new_s_P_Indiglo;
                  fired |= ARENA_P_Indiglo; // Stable target
                  // Internal Event Lifeline: Next Small Step
                  internal.cycle();
                  break 'arena_P_Indiglo;
                }
              },
              State_P_Indiglo::S_Pushed(ref mut s_P_Indiglo_Pushed) => {
                // Outgoing transition 0
                // A transition may have fired earlier that overlaps with our arena:
                if fired & (ARENA_P_Indiglo) == ARENA_NONE {
                  if let Some(InEvent::E_topRightReleased) = &input {
                    // Exit actions
                    s_P_Indiglo_Pushed.exit_current(&mut sc.timers, scope, internal, sched, output);
                    // Enter actions
                    State_P_Indiglo_Released::enter_default(&mut sc.timers, scope, internal, sched, output);
                    // Build new state configuration
                    let new_s_P_Indiglo_Released: State_P_Indiglo_Released = Default::default();
                    let new_s_P_Indiglo = State_P_Indiglo::S_Released(new_s_P_Indiglo_Released);
                    // Update arena configuration
                    *s_P_Indiglo = new_s_P_Indiglo;
                    fired |= ARENA_P_Indiglo; // Stable target
                    // Internal Event Lifeline: Next Small Step
                    internal.cycle();
                    break 'arena_P_Indiglo;
                  }
                }
              },
              State_P_Indiglo::S_Released(ref mut s_P_Indiglo_Released) => {
                // Outgoing transition 0
                // A transition may have fired earlier that overlaps with our arena:
                if fired & (ARENA_P_Indiglo) == ARENA_NONE {
                  if let Some(InEvent::E_topRightPressed) = &input {
                    // Exit actions
                    s_P_Indiglo_Released.exit_current(&mut sc.timers, scope, internal, sched, output);
                    // Enter actions
                    State_P_Indiglo_Pushed::enter_default(&mut sc.timers, scope, internal, sched, output);
                    // Build new state configuration
                    let new_s_P_Indiglo_Pushed: State_P_Indiglo_Pushed = Default::default();
                    let new_s_P_Indiglo = State_P_Indiglo::S_Pushed(new_s_P_Indiglo_Pushed);
                    // Update arena configuration
                    *s_P_Indiglo = new_s_P_Indiglo;
                    fired |= ARENA_P_Indiglo; // Stable target
                    // Internal Event Lifeline: Next Small Step
                    internal.cycle();
                    break 'arena_P_Indiglo;
                  }
                }
                // Outgoing transition 1
                // A transition may have fired earlier that overlaps with our arena:
                if fired & (ARENA_P_Indiglo) == ARENA_NONE {
                  if let Some(InEvent::A3) = &input {
                    // Exit actions
                    s_P_Indiglo_Released.exit_current(&mut sc.timers, scope, internal, sched, output);
                    // Transition's actions
                    (output)(OutEvent::E_unsetIndiglo);
                    // Enter actions
                    State_P_Indiglo_Off::enter_default(&mut sc.timers, scope, internal, sched, output);
                    // Build new state configuration
                    let new_s_P_Indiglo_Off: State_P_Indiglo_Off = Default::default();
                    let new_s_P_Indiglo = State_P_Indiglo::S_Off(new_s_P_Indiglo_Off);
                    // Update arena configuration
                    *s_P_Indiglo = new_s_P_Indiglo;
                    fired |= ARENA_P_Indiglo; // Stable target
                    // Internal Event Lifeline: Next Small Step
                    internal.cycle();
                    break 'arena_P_Indiglo;
                  }
                }
              },
            };
            break;
          }
        }
        // Orthogonal region
        if (fired | dirty) & ARENA_P_ChronoWrapper == ARENA_NONE {
          'arena_P_ChronoWrapper: loop {
            match *s_P_ChronoWrapper {
              State_P_ChronoWrapper::S_Chrono(ref mut s_P_ChronoWrapper_Chrono) => {
                // Outgoing transition 0
                if let Some(InEvent::E_bottomLeftPressed) = &input {
                  if f2_guard((*s_P_Alarm, *s_P_Indiglo, *s_P_Display, *s_P_Time, ), ) {
                    // Exit actions
                    s_P_ChronoWrapper_Chrono.exit_current(&mut sc.timers, scope, internal, sched, output);
                    // Transition's actions
                    (output)(OutEvent::E_resetChrono);
                    internal.raise().e_int_refresh_chrono = Some(Event_int_refresh_chrono{});
                    // Enter actions
                    State_P_ChronoWrapper_Chrono::enter_actions(&mut sc.timers, scope, internal, sched, output);
                    State_P_ChronoWrapper_Chrono_Stopped::enter_default(&mut sc.timers, scope, internal, sched, output);
                    // Build new state configuration
                    let new_s_P_ChronoWrapper_Chrono_Stopped: State_P_ChronoWrapper_Chrono_Stopped = Default::default();
                    let new_s_P_ChronoWrapper_Chrono = State_P_ChronoWrapper_Chrono::S_Stopped(new_s_P_ChronoWrapper_Chrono_Stopped);
                    let new_s_P_ChronoWrapper = State_P_ChronoWrapper::S_Chrono(new_s_P_ChronoWrapper_Chrono);
                    // Update arena configuration
                    *s_P_ChronoWrapper = new_s_P_ChronoWrapper;
                    fired |= ARENA_P_ChronoWrapper; // Stable target
                    // Internal Event Lifeline: Next Small Step
                    internal.cycle();
                    break 'arena_P_ChronoWrapper;
                  }
                }
                if (fired | dirty) & ARENA_P_ChronoWrapper_Chrono == ARENA_NONE {
                  'arena_P_ChronoWrapper_Chrono: loop {
                    match *s_P_ChronoWrapper_Chrono {
                      State_P_ChronoWrapper_Chrono::S_Stopped(ref mut s_P_ChronoWrapper_Chrono_Stopped) => {
                        // Outgoing transition 0
                        if let Some(InEvent::E_bottomRightPressed) = &input {
                          if f3_guard((*s_P_Alarm, *s_P_Indiglo, *s_P_Display, *s_P_Time, ), ) {
                            // Exit actions
                            s_P_ChronoWrapper_Chrono_Stopped.exit_current(&mut sc.timers, scope, internal, sched, output);
                            // Enter actions
                            State_P_ChronoWrapper_Chrono_Running::enter_default(&mut sc.timers, scope, internal, sched, output);
                            // Build new state configuration
                            let new_s_P_ChronoWrapper_Chrono_Running: State_P_ChronoWrapper_Chrono_Running = Default::default();
                            let new_s_P_ChronoWrapper_Chrono = State_P_ChronoWrapper_Chrono::S_Running(new_s_P_ChronoWrapper_Chrono_Running);
                            // Update arena configuration
                            *s_P_ChronoWrapper_Chrono = new_s_P_ChronoWrapper_Chrono;
                            fired |= ARENA_P_ChronoWrapper_Chrono; // Stable target
                            // Internal Event Lifeline: Next Small Step
                            internal.cycle();
                            break 'arena_P_ChronoWrapper_Chrono;
                          }
                        }
                      },
                      State_P_ChronoWrapper_Chrono::S_Running(ref mut s_P_ChronoWrapper_Chrono_Running) => {
                        // Outgoing transition 0
                        // A transition may have fired earlier that overlaps with our arena:
                        if fired & (ARENA_P_ChronoWrapper_Chrono) == ARENA_NONE {
                          if let Some(InEvent::A4) = &input {
                            // Exit actions
                            s_P_ChronoWrapper_Chrono_Running.exit_current(&mut sc.timers, scope, internal, sched, output);
                            // Transition's actions
                            (output)(OutEvent::E_increaseChronoByOne);
                            internal.raise().e_int_refresh_chrono = Some(Event_int_refresh_chrono{});
                            // Enter actions
                            State_P_ChronoWrapper_Chrono_Running::enter_default(&mut sc.timers, scope, internal, sched, output);
                            // Build new state configuration
                            let new_s_P_ChronoWrapper_Chrono_Running: State_P_ChronoWrapper_Chrono_Running = Default::default();
                            let new_s_P_ChronoWrapper_Chrono = State_P_ChronoWrapper_Chrono::S_Running(new_s_P_ChronoWrapper_Chrono_Running);
                            // Update arena configuration
                            *s_P_ChronoWrapper_Chrono = new_s_P_ChronoWrapper_Chrono;
                            fired |= ARENA_P_ChronoWrapper_Chrono; // Stable target
                            // Internal Event Lifeline: Next Small Step
                            internal.cycle();
                            break 'arena_P_ChronoWrapper_Chrono;
                          }
                        }
                        // Outgoing transition 1
                        // A transition may have fired earlier that overlaps with our arena:
                        if fired & (ARENA_P_ChronoWrapper_Chrono) == ARENA_NONE {
                          if let Some(InEvent::E_bottomRightPressed) = &input {
                            if f4_guard((*s_P_Alarm, *s_P_Indiglo, *s_P_Display, *s_P_Time, ), ) {
                              // Exit actions
                              s_P_ChronoWrapper_Chrono_Running.exit_current(&mut sc.timers, scope, internal, sched, output);
                              // Enter actions
                              State_P_ChronoWrapper_Chrono_Stopped::enter_default(&mut sc.timers, scope, internal, sched, output);
                              // Build new state configuration
                              let new_s_P_ChronoWrapper_Chrono_Stopped: State_P_ChronoWrapper_Chrono_Stopped = Default::default();
                              let new_s_P_ChronoWrapper_Chrono = State_P_ChronoWrapper_Chrono::S_Stopped(new_s_P_ChronoWrapper_Chrono_Stopped);
                              // Update arena configuration
                              *s_P_ChronoWrapper_Chrono = new_s_P_ChronoWrapper_Chrono;
                              fired |= ARENA_P_ChronoWrapper_Chrono; // Stable target
                              // Internal Event Lifeline: Next Small Step
                              internal.cycle();
                              break 'arena_P_ChronoWrapper_Chrono;
                            }
                          }
                        }
                      },
                    };
                    break;
                  }
                }
              },
            };
            break;
          }
        }
        // Orthogonal region
        if (fired | dirty) & ARENA_P_Display == ARENA_NONE {
          'arena_P_Display: loop {
            match *s_P_Display {
              State_P_Display::S_TimeUpdate(ref mut s_P_Display_TimeUpdate) => {
                // Outgoing transition 0
                if let Some(Event_int_refresh_time) = &internal.current().e_int_refresh_time {
                  // Exit actions
                  s_P_Display_TimeUpdate.exit_current(&mut sc.timers, scope, internal, sched, output);
                  // Enter actions
                  State_P_Display_TimeUpdate::enter_default(&mut sc.timers, scope, internal, sched, output);
                  // Build new state configuration
                  let new_s_P_Display_TimeUpdate: State_P_Display_TimeUpdate = Default::default();
                  let new_s_P_Display = State_P_Display::S_TimeUpdate(new_s_P_Display_TimeUpdate);
                  // Update arena configuration
                  *s_P_Display = new_s_P_Display;
                  fired |= ARENA_P_Display; // Stable target
                  // Internal Event Lifeline: Next Small Step
                  internal.cycle();
                  break 'arena_P_Display;
                }
                // Outgoing transition 1
                // A transition may have fired earlier that overlaps with our arena:
                if fired & (ARENA_P_Display) == ARENA_NONE {
                  if let Some(InEvent::E_topLeftPressed) = &input {
                    // Exit actions
                    s_P_Display_TimeUpdate.exit_current(&mut sc.timers, scope, internal, sched, output);
                    // Enter actions
                    State_P_Display_ChronoUpdate::enter_default(&mut sc.timers, scope, internal, sched, output);
                    // Build new state configuration
                    let new_s_P_Display_ChronoUpdate: State_P_Display_ChronoUpdate = Default::default();
                    let new_s_P_Display = State_P_Display::S_ChronoUpdate(new_s_P_Display_ChronoUpdate);
                    // Update arena configuration
                    *s_P_Display = new_s_P_Display;
                    fired |= ARENA_P_Display; // Stable target
                    // Internal Event Lifeline: Next Small Step
                    internal.cycle();
                    break 'arena_P_Display;
                  }
                }
                // Outgoing transition 2
                // A transition may have fired earlier that overlaps with our arena:
                if fired & (ARENA_P_Display) == ARENA_NONE {
                  if let Some(InEvent::E_bottomRightPressed) = &input {
                    // Exit actions
                    s_P_Display_TimeUpdate.exit_current(&mut sc.timers, scope, internal, sched, output);
                    // Enter actions
                    State_P_Display_WaitingToEdit::enter_default(&mut sc.timers, scope, internal, sched, output);
                    // Build new state configuration
                    let new_s_P_Display_WaitingToEdit: State_P_Display_WaitingToEdit = Default::default();
                    let new_s_P_Display = State_P_Display::S_WaitingToEdit(new_s_P_Display_WaitingToEdit);
                    // Update arena configuration
                    *s_P_Display = new_s_P_Display;
                    fired |= ARENA_P_Display; // Stable target
                    // Internal Event Lifeline: Next Small Step
                    internal.cycle();
                    break 'arena_P_Display;
                  }
                }
                // Outgoing transition 3
                // A transition may have fired earlier that overlaps with our arena:
                if fired & (ARENA_P_Display) == ARENA_NONE {
                  if let Some(InEvent::E_bottomLeftPressed) = &input {
                    // Exit actions
                    s_P_Display_TimeUpdate.exit_current(&mut sc.timers, scope, internal, sched, output);
                    // Enter actions
                    State_P_Display_WaitingForAlarm::enter_default(&mut sc.timers, scope, internal, sched, output);
                    // Build new state configuration
                    let new_s_P_Display_WaitingForAlarm: State_P_Display_WaitingForAlarm = Default::default();
                    let new_s_P_Display = State_P_Display::S_WaitingForAlarm(new_s_P_Display_WaitingForAlarm);
                    // Update arena configuration
                    *s_P_Display = new_s_P_Display;
                    fired |= ARENA_P_Display; // Stable target
                    // Internal Event Lifeline: Next Small Step
                    internal.cycle();
                    break 'arena_P_Display;
                  }
                }
              },
              State_P_Display::S_WaitingToEdit(ref mut s_P_Display_WaitingToEdit) => {
                // Outgoing transition 0
                // A transition may have fired earlier that overlaps with our arena:
                if fired & (ARENA_P_Display) == ARENA_NONE {
                  if let Some(InEvent::A5) = &input {
                    // Exit actions
                    s_P_Display_WaitingToEdit.exit_current(&mut sc.timers, scope, internal, sched, output);
                    // Enter actions
                    State_P_Display_EditingTime::enter_default(&mut sc.timers, scope, internal, sched, output);
                    // Build new state configuration
                    let new_s_P_Display_EditingTime: State_P_Display_EditingTime = Default::default();
                    let new_s_P_Display = State_P_Display::S_EditingTime(new_s_P_Display_EditingTime);
                    // Update arena configuration
                    *s_P_Display = new_s_P_Display;
                    fired |= ARENA_P_Display; // Stable target
                    // Internal Event Lifeline: Next Small Step
                    internal.cycle();
                    break 'arena_P_Display;
                  }
                }
                // Outgoing transition 1
                // A transition may have fired earlier that overlaps with our arena:
                if fired & (ARENA_P_Display) == ARENA_NONE {
                  if let Some(InEvent::E_bottomRightReleased) = &input {
                    // Exit actions
                    s_P_Display_WaitingToEdit.exit_current(&mut sc.timers, scope, internal, sched, output);
                    // Enter actions
                    State_P_Display_TimeUpdate::enter_default(&mut sc.timers, scope, internal, sched, output);
                    // Build new state configuration
                    let new_s_P_Display_TimeUpdate: State_P_Display_TimeUpdate = Default::default();
                    let new_s_P_Display = State_P_Display::S_TimeUpdate(new_s_P_Display_TimeUpdate);
                    // Update arena configuration
                    *s_P_Display = new_s_P_Display;
                    fired |= ARENA_P_Display; // Stable target
                    // Internal Event Lifeline: Next Small Step
                    internal.cycle();
                    break 'arena_P_Display;
                  }
                }
              },
              State_P_Display::S_WaitingForAlarm(ref mut s_P_Display_WaitingForAlarm) => {
                // Outgoing transition 0
                // A transition may have fired earlier that overlaps with our arena:
                if fired & (ARENA_P_Display) == ARENA_NONE {
                  if let Some(InEvent::A6) = &input {
                    // Exit actions
                    s_P_Display_WaitingForAlarm.exit_current(&mut sc.timers, scope, internal, sched, output);
                    // Transition's actions
                    internal.raise().e_alarm_edit = Some(Event_alarm_edit{});
                    // Enter actions
                    State_P_Display_EditingTime::enter_default(&mut sc.timers, scope, internal, sched, output);
                    // Build new state configuration
                    let new_s_P_Display_EditingTime: State_P_Display_EditingTime = Default::default();
                    let new_s_P_Display = State_P_Display::S_EditingTime(new_s_P_Display_EditingTime);
                    // Update arena configuration
                    *s_P_Display = new_s_P_Display;
                    fired |= ARENA_P_Display; // Stable target
                    // Internal Event Lifeline: Next Small Step
                    internal.cycle();
                    break 'arena_P_Display;
                  }
                }
                // Outgoing transition 1
                // A transition may have fired earlier that overlaps with our arena:
                if fired & (ARENA_P_Display) == ARENA_NONE {
                  if let Some(InEvent::E_bottomLeftReleased) = &input {
                    // Exit actions
                    s_P_Display_WaitingForAlarm.exit_current(&mut sc.timers, scope, internal, sched, output);
                    // Enter actions
                    State_P_Display_TimeUpdate::enter_default(&mut sc.timers, scope, internal, sched, output);
                    // Build new state configuration
                    let new_s_P_Display_TimeUpdate: State_P_Display_TimeUpdate = Default::default();
                    let new_s_P_Display = State_P_Display::S_TimeUpdate(new_s_P_Display_TimeUpdate);
                    // Update arena configuration
                    *s_P_Display = new_s_P_Display;
                    fired |= ARENA_P_Display; // Stable target
                    // Internal Event Lifeline: Next Small Step
                    internal.cycle();
                    break 'arena_P_Display;
                  }
                }
              },
              State_P_Display::S_EditingTime(ref mut s_P_Display_EditingTime) => {
                if (fired | dirty) & ARENA_P_Display_EditingTime == ARENA_NONE {
                  'arena_P_Display_EditingTime: loop {
                    match *s_P_Display_EditingTime {
                      State_P_Display_EditingTime::S_Waiting(ref mut s_P_Display_EditingTime_Waiting) => {
                        // Outgoing transition 0
                        if let Some(InEvent::E_bottomLeftPressed) = &input {
                          // Exit actions
                          s_P_Display_EditingTime_Waiting.exit_current(&mut sc.timers, scope, internal, sched, output);
                          // Enter actions
                          State_P_Display_EditingTime_Increasing::enter_default(&mut sc.timers, scope, internal, sched, output);
                          // Build new state configuration
                          let new_s_P_Display_EditingTime_Increasing: State_P_Display_EditingTime_Increasing = Default::default();
                          let new_s_P_Display_EditingTime = State_P_Display_EditingTime::S_Increasing(new_s_P_Display_EditingTime_Increasing);
                          // Update arena configuration
                          *s_P_Display_EditingTime = new_s_P_Display_EditingTime;
                          fired |= ARENA_P_Display_EditingTime; // Stable target
                          // Internal Event Lifeline: Next Small Step
                          internal.cycle();
                          break 'arena_P_Display_EditingTime;
                        }
                        // Outgoing transition 1
                        // A transition may have fired earlier that overlaps with our arena:
                        if fired & (ARENA_P_Display_EditingTime) == ARENA_NONE {
                          if let Some(InEvent::E_bottomRightPressed) = &input {
                            // Exit actions
                            s_P_Display_EditingTime_Waiting.exit_current(&mut sc.timers, scope, internal, sched, output);
                            // Enter actions
                            State_P_Display_EditingTime_GoingToNext::enter_default(&mut sc.timers, scope, internal, sched, output);
                            // Build new state configuration
                            let new_s_P_Display_EditingTime_GoingToNext: State_P_Display_EditingTime_GoingToNext = Default::default();
                            let new_s_P_Display_EditingTime = State_P_Display_EditingTime::S_GoingToNext(new_s_P_Display_EditingTime_GoingToNext);
                            // Update arena configuration
                            *s_P_Display_EditingTime = new_s_P_Display_EditingTime;
                            fired |= ARENA_P_Display_EditingTime; // Stable target
                            // Internal Event Lifeline: Next Small Step
                            internal.cycle();
                            break 'arena_P_Display_EditingTime;
                          }
                        }
                        // Outgoing transition 2
                        // A transition may have fired earlier that overlaps with our arena:
                        if fired & (ARENA_P_Display) == ARENA_NONE {
                          if let Some(InEvent::A7) = &input {
                            // Exit actions
                            s_P_Display_EditingTime_Waiting.exit_current(&mut sc.timers, scope, internal, sched, output);
                            State_P_Display_EditingTime::exit_actions(&mut sc.timers, scope, internal, sched, output);
                            // Enter actions
                            State_P_Display_TimeUpdate::enter_default(&mut sc.timers, scope, internal, sched, output);
                            // Build new state configuration
                            let new_s_P_Display_TimeUpdate: State_P_Display_TimeUpdate = Default::default();
                            let new_s_P_Display = State_P_Display::S_TimeUpdate(new_s_P_Display_TimeUpdate);
                            // Update arena configuration
                            *s_P_Display = new_s_P_Display;
                            fired |= ARENA_P_Display; // Stable target
                            // Internal Event Lifeline: Next Small Step
                            internal.cycle();
                            break 'arena_P_Display;
                          }
                        }
                      },
                      State_P_Display_EditingTime::S_GoingToNext(ref mut s_P_Display_EditingTime_GoingToNext) => {
                        // Outgoing transition 0
                        // A transition may have fired earlier that overlaps with our arena:
                        if fired & (ARENA_P_Display_EditingTime) == ARENA_NONE {
                          if let Some(InEvent::E_bottomRightReleased) = &input {
                            // Exit actions
                            s_P_Display_EditingTime_GoingToNext.exit_current(&mut sc.timers, scope, internal, sched, output);
                            // Transition's actions
                            (output)(OutEvent::E_selectNext);
                            // Enter actions
                            State_P_Display_EditingTime_Waiting::enter_default(&mut sc.timers, scope, internal, sched, output);
                            // Build new state configuration
                            let new_s_P_Display_EditingTime_Waiting: State_P_Display_EditingTime_Waiting = Default::default();
                            let new_s_P_Display_EditingTime = State_P_Display_EditingTime::S_Waiting(new_s_P_Display_EditingTime_Waiting);
                            // Update arena configuration
                            *s_P_Display_EditingTime = new_s_P_Display_EditingTime;
                            fired |= ARENA_P_Display_EditingTime; // Stable target
                            // Internal Event Lifeline: Next Small Step
                            internal.cycle();
                            break 'arena_P_Display_EditingTime;
                          }
                        }
                        // Outgoing transition 1
                        // A transition may have fired earlier that overlaps with our arena:
                        if fired & (ARENA_P_Display) == ARENA_NONE {
                          if let Some(InEvent::A8) = &input {
                            // Exit actions
                            s_P_Display_EditingTime_GoingToNext.exit_current(&mut sc.timers, scope, internal, sched, output);
                            State_P_Display_EditingTime::exit_actions(&mut sc.timers, scope, internal, sched, output);
                            // Enter actions
                            State_P_Display_TimeUpdate::enter_default(&mut sc.timers, scope, internal, sched, output);
                            // Build new state configuration
                            let new_s_P_Display_TimeUpdate: State_P_Display_TimeUpdate = Default::default();
                            let new_s_P_Display = State_P_Display::S_TimeUpdate(new_s_P_Display_TimeUpdate);
                            // Update arena configuration
                            *s_P_Display = new_s_P_Display;
                            fired |= ARENA_P_Display; // Stable target
                            // Internal Event Lifeline: Next Small Step
                            internal.cycle();
                            break 'arena_P_Display;
                          }
                        }
                      },
                      State_P_Display_EditingTime::S_Increasing(ref mut s_P_Display_EditingTime_Increasing) => {
                        // Outgoing transition 0
                        // A transition may have fired earlier that overlaps with our arena:
                        if fired & (ARENA_P_Display_EditingTime) == ARENA_NONE {
                          if let Some(InEvent::A9) = &input {
                            // Exit actions
                            s_P_Display_EditingTime_Increasing.exit_current(&mut sc.timers, scope, internal, sched, output);
                            // Enter actions
                            State_P_Display_EditingTime_Increasing::enter_default(&mut sc.timers, scope, internal, sched, output);
                            // Build new state configuration
                            let new_s_P_Display_EditingTime_Increasing: State_P_Display_EditingTime_Increasing = Default::default();
                            let new_s_P_Display_EditingTime = State_P_Display_EditingTime::S_Increasing(new_s_P_Display_EditingTime_Increasing);
                            // Update arena configuration
                            *s_P_Display_EditingTime = new_s_P_Display_EditingTime;
                            fired |= ARENA_P_Display_EditingTime; // Stable target
                            // Internal Event Lifeline: Next Small Step
                            internal.cycle();
                            break 'arena_P_Display_EditingTime;
                          }
                        }
                        // Outgoing transition 1
                        // A transition may have fired earlier that overlaps with our arena:
                        if fired & (ARENA_P_Display_EditingTime) == ARENA_NONE {
                          if let Some(InEvent::E_bottomLeftReleased) = &input {
                            // Exit actions
                            s_P_Display_EditingTime_Increasing.exit_current(&mut sc.timers, scope, internal, sched, output);
                            // Enter actions
                            State_P_Display_EditingTime_Waiting::enter_default(&mut sc.timers, scope, internal, sched, output);
                            // Build new state configuration
                            let new_s_P_Display_EditingTime_Waiting: State_P_Display_EditingTime_Waiting = Default::default();
                            let new_s_P_Display_EditingTime = State_P_Display_EditingTime::S_Waiting(new_s_P_Display_EditingTime_Waiting);
                            // Update arena configuration
                            *s_P_Display_EditingTime = new_s_P_Display_EditingTime;
                            fired |= ARENA_P_Display_EditingTime; // Stable target
                            // Internal Event Lifeline: Next Small Step
                            internal.cycle();
                            break 'arena_P_Display_EditingTime;
                          }
                        }
                      },
                    };
                    break;
                  }
                }
              },
              State_P_Display::S_ChronoUpdate(ref mut s_P_Display_ChronoUpdate) => {
                // Outgoing transition 0
                // A transition may have fired earlier that overlaps with our arena:
                if fired & (ARENA_P_Display) == ARENA_NONE {
                  if let Some(InEvent::E_topLeftPressed) = &input {
                    // Exit actions
                    s_P_Display_ChronoUpdate.exit_current(&mut sc.timers, scope, internal, sched, output);
                    // Enter actions
                    State_P_Display_TimeUpdate::enter_default(&mut sc.timers, scope, internal, sched, output);
                    // Build new state configuration
                    let new_s_P_Display_TimeUpdate: State_P_Display_TimeUpdate = Default::default();
                    let new_s_P_Display = State_P_Display::S_TimeUpdate(new_s_P_Display_TimeUpdate);
                    // Update arena configuration
                    *s_P_Display = new_s_P_Display;
                    fired |= ARENA_P_Display; // Stable target
                    // Internal Event Lifeline: Next Small Step
                    internal.cycle();
                    break 'arena_P_Display;
                  }
                }
                // Outgoing transition 1
                // A transition may have fired earlier that overlaps with our arena:
                if fired & (ARENA_P_Display) == ARENA_NONE {
                  if let Some(Event_int_refresh_chrono) = &internal.current().e_int_refresh_chrono {
                    // Exit actions
                    s_P_Display_ChronoUpdate.exit_current(&mut sc.timers, scope, internal, sched, output);
                    // Enter actions
                    State_P_Display_ChronoUpdate::enter_default(&mut sc.timers, scope, internal, sched, output);
                    // Build new state configuration
                    let new_s_P_Display_ChronoUpdate: State_P_Display_ChronoUpdate = Default::default();
                    let new_s_P_Display = State_P_Display::S_ChronoUpdate(new_s_P_Display_ChronoUpdate);
                    // Update arena configuration
                    *s_P_Display = new_s_P_Display;
                    fired |= ARENA_P_Display; // Stable target
                    // Internal Event Lifeline: Next Small Step
                    internal.cycle();
                    break 'arena_P_Display;
                  }
                }
              },
            };
            break;
          }
        }
        // Orthogonal region
        if (fired | dirty) & ARENA_P_Time == ARENA_NONE {
          'arena_P_Time: loop {
            match *s_P_Time {
              State_P_Time::S_Increasing(ref mut s_P_Time_Increasing) => {
                // Outgoing transition 0
                if let Some(InEvent::A10) = &input {
                  // Exit actions
                  s_P_Time_Increasing.exit_current(&mut sc.timers, scope, internal, sched, output);
                  // Transition's actions
                  (output)(OutEvent::E_increaseTimeByOne);
                  (output)(OutEvent::E_checkTime);
                  internal.raise().e_int_refresh_time = Some(Event_int_refresh_time{});
                  // Enter actions
                  State_P_Time_Increasing::enter_default(&mut sc.timers, scope, internal, sched, output);
                  // Build new state configuration
                  let new_s_P_Time_Increasing: State_P_Time_Increasing = Default::default();
                  let new_s_P_Time = State_P_Time::S_Increasing(new_s_P_Time_Increasing);
                  // Update arena configuration
                  *s_P_Time = new_s_P_Time;
                  fired |= ARENA_P_Time; // Stable target
                  // Internal Event Lifeline: Next Small Step
                  internal.cycle();
                  break 'arena_P_Time;
                }
                // Outgoing transition 1
                // A transition may have fired earlier that overlaps with our arena:
                if fired & (ARENA_P_Time) == ARENA_NONE {
                  if let Some(Event_time_edit) = &internal.current().e_time_edit {
                    // Exit actions
                    s_P_Time_Increasing.exit_current(&mut sc.timers, scope, internal, sched, output);
                    // Enter actions
                    State_P_Time_Editing::enter_default(&mut sc.timers, scope, internal, sched, output);
                    // Build new state configuration
                    let new_s_P_Time_Editing: State_P_Time_Editing = Default::default();
                    let new_s_P_Time = State_P_Time::S_Editing(new_s_P_Time_Editing);
                    // Update arena configuration
                    *s_P_Time = new_s_P_Time;
                    fired |= ARENA_P_Time; // Stable target
                    // Internal Event Lifeline: Next Small Step
                    internal.cycle();
                    break 'arena_P_Time;
                  }
                }
              },
              State_P_Time::S_Editing(ref mut s_P_Time_Editing) => {
                // Outgoing transition 0
                // A transition may have fired earlier that overlaps with our arena:
                if fired & (ARENA_P_Time) == ARENA_NONE {
                  if let Some(Event_edit_done) = &internal.current().e_edit_done {
                    // Exit actions
                    s_P_Time_Editing.exit_current(&mut sc.timers, scope, internal, sched, output);
                    // Enter actions
                    State_P_Time_Increasing::enter_default(&mut sc.timers, scope, internal, sched, output);
                    // Build new state configuration
                    let new_s_P_Time_Increasing: State_P_Time_Increasing = Default::default();
                    let new_s_P_Time = State_P_Time::S_Increasing(new_s_P_Time_Increasing);
                    // Update arena configuration
                    *s_P_Time = new_s_P_Time;
                    fired |= ARENA_P_Time; // Stable target
                    // Internal Event Lifeline: Next Small Step
                    internal.cycle();
                    break 'arena_P_Time;
                  }
                }
              },
            };
            break;
          }
        }
      },
    };
    break;
  }
  fired
}
fn combo_step<Sched: statechart::Scheduler<InEvent=InEvent>>(sc: &mut Statechart<Sched>, input: &mut Option<InEvent>, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent), dirty: Arenas) -> Arenas {
  // Combo-Step Maximality: TAKE_ONE
  fair_step(sc, input, internal, sched, output, dirty)
}
fn big_step<Sched: statechart::Scheduler<InEvent=InEvent>>(sc: &mut Statechart<Sched>, input: &mut Option<InEvent>, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent), dirty: Arenas) -> Arenas {
  // Big-Step Maximality: TAKE_ONE
  combo_step(sc, input, internal, sched, output, dirty)
}

impl<Sched: statechart::Scheduler<InEvent=InEvent>> statechart::SC for Statechart<Sched> {
  type InEvent = InEvent;
  type OutEvent = OutEvent;
  type Sched = Sched;

  fn init(&mut self, sched: &mut Self::Sched, output: &mut impl FnMut(Self::OutEvent)) {
    Root::enter_default(&mut self.timers, &mut self.data, &mut Default::default(), sched, output)
  }
  fn big_step(&mut self, mut input: Option<InEvent>, sched: &mut Self::Sched, output: &mut impl FnMut(Self::OutEvent)) {
    let mut internal: InternalLifeline = Default::default();
    big_step(self, &mut input, &mut internal, sched, output, ARENA_NONE);
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_Alarm_Off {
}
impl State_P_Alarm_Off {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm_Off::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm_Off::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm_Off::enter_actions(timers, data, internal, sched, output);
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_Alarm_On_NotBlinking {
}
impl State_P_Alarm_On_NotBlinking {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm_On_NotBlinking::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm_On_NotBlinking::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm_On_NotBlinking::enter_actions(timers, data, internal, sched, output);
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_Alarm_On_Blinking_On {
}
impl State_P_Alarm_On_Blinking_On {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    (output)(OutEvent::E_setIndiglo);
    timers[0] = sched.set_timeout(500, InEvent::A0);
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    sched.unset_timeout(&timers[0]);
    (output)(OutEvent::E_unsetIndiglo);
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm_On_Blinking_On::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm_On_Blinking_On::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm_On_Blinking_On::enter_actions(timers, data, internal, sched, output);
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_Alarm_On_Blinking_Off {
}
impl State_P_Alarm_On_Blinking_Off {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    timers[1] = sched.set_timeout(500, InEvent::A1);
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    sched.unset_timeout(&timers[1]);
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm_On_Blinking_Off::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm_On_Blinking_Off::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm_On_Blinking_Off::enter_actions(timers, data, internal, sched, output);
  }
}

// Or-state
#[derive(Copy, Clone)]
enum State_P_Alarm_On_Blinking {
  S_On(State_P_Alarm_On_Blinking_On),
  S_Off(State_P_Alarm_On_Blinking_Off),
}
impl Default for State_P_Alarm_On_Blinking {
  fn default() -> Self {
    Self::S_On(Default::default())
  }
}
impl State_P_Alarm_On_Blinking {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    timers[2] = sched.set_timeout(4000, InEvent::A2);
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    sched.unset_timeout(&timers[2]);
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm_On_Blinking::enter_actions(timers, data, internal, sched, output);
    State_P_Alarm_On_Blinking_On::enter_default(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    match self {
      Self::S_On(s) => { s.exit_current(timers, data, internal, sched, output); },
      Self::S_Off(s) => { s.exit_current(timers, data, internal, sched, output); },
    }
    State_P_Alarm_On_Blinking::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm_On_Blinking::enter_actions(timers, data, internal, sched, output);
    match self {
      Self::S_On(s) => { s.enter_current(timers, data, internal, sched, output); },
      Self::S_Off(s) => { s.enter_current(timers, data, internal, sched, output); },
    }
  }
}

// Or-state
#[derive(Copy, Clone)]
enum State_P_Alarm_On {
  S_NotBlinking(State_P_Alarm_On_NotBlinking),
  S_Blinking(State_P_Alarm_On_Blinking),
}
impl Default for State_P_Alarm_On {
  fn default() -> Self {
    Self::S_NotBlinking(Default::default())
  }
}
impl State_P_Alarm_On {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    (output)(OutEvent::E_setAlarm);
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    (output)(OutEvent::E_setAlarm);
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm_On::enter_actions(timers, data, internal, sched, output);
    State_P_Alarm_On_NotBlinking::enter_default(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    match self {
      Self::S_NotBlinking(s) => { s.exit_current(timers, data, internal, sched, output); },
      Self::S_Blinking(s) => { s.exit_current(timers, data, internal, sched, output); },
    }
    State_P_Alarm_On::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm_On::enter_actions(timers, data, internal, sched, output);
    match self {
      Self::S_NotBlinking(s) => { s.enter_current(timers, data, internal, sched, output); },
      Self::S_Blinking(s) => { s.enter_current(timers, data, internal, sched, output); },
    }
  }
}

// Or-state
#[derive(Copy, Clone)]
enum State_P_Alarm {
  S_Off(State_P_Alarm_Off),
  S_On(State_P_Alarm_On),
}
impl Default for State_P_Alarm {
  fn default() -> Self {
    Self::S_Off(Default::default())
  }
}
impl State_P_Alarm {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm::enter_actions(timers, data, internal, sched, output);
    State_P_Alarm_Off::enter_default(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    match self {
      Self::S_Off(s) => { s.exit_current(timers, data, internal, sched, output); },
      Self::S_On(s) => { s.exit_current(timers, data, internal, sched, output); },
    }
    State_P_Alarm::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Alarm::enter_actions(timers, data, internal, sched, output);
    match self {
      Self::S_Off(s) => { s.enter_current(timers, data, internal, sched, output); },
      Self::S_On(s) => { s.enter_current(timers, data, internal, sched, output); },
    }
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_Indiglo_Off {
}
impl State_P_Indiglo_Off {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Indiglo_Off::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Indiglo_Off::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Indiglo_Off::enter_actions(timers, data, internal, sched, output);
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_Indiglo_Pushed {
}
impl State_P_Indiglo_Pushed {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Indiglo_Pushed::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Indiglo_Pushed::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Indiglo_Pushed::enter_actions(timers, data, internal, sched, output);
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_Indiglo_Released {
}
impl State_P_Indiglo_Released {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    timers[3] = sched.set_timeout(2000, InEvent::A3);
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    sched.unset_timeout(&timers[3]);
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Indiglo_Released::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Indiglo_Released::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Indiglo_Released::enter_actions(timers, data, internal, sched, output);
  }
}

// Or-state
#[derive(Copy, Clone)]
enum State_P_Indiglo {
  S_Off(State_P_Indiglo_Off),
  S_Pushed(State_P_Indiglo_Pushed),
  S_Released(State_P_Indiglo_Released),
}
impl Default for State_P_Indiglo {
  fn default() -> Self {
    Self::S_Off(Default::default())
  }
}
impl State_P_Indiglo {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Indiglo::enter_actions(timers, data, internal, sched, output);
    State_P_Indiglo_Off::enter_default(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    match self {
      Self::S_Off(s) => { s.exit_current(timers, data, internal, sched, output); },
      Self::S_Pushed(s) => { s.exit_current(timers, data, internal, sched, output); },
      Self::S_Released(s) => { s.exit_current(timers, data, internal, sched, output); },
    }
    State_P_Indiglo::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Indiglo::enter_actions(timers, data, internal, sched, output);
    match self {
      Self::S_Off(s) => { s.enter_current(timers, data, internal, sched, output); },
      Self::S_Pushed(s) => { s.enter_current(timers, data, internal, sched, output); },
      Self::S_Released(s) => { s.enter_current(timers, data, internal, sched, output); },
    }
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_ChronoWrapper_Chrono_Stopped {
}
impl State_P_ChronoWrapper_Chrono_Stopped {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_ChronoWrapper_Chrono_Stopped::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_ChronoWrapper_Chrono_Stopped::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_ChronoWrapper_Chrono_Stopped::enter_actions(timers, data, internal, sched, output);
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_ChronoWrapper_Chrono_Running {
}
impl State_P_ChronoWrapper_Chrono_Running {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    timers[4] = sched.set_timeout(10, InEvent::A4);
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    sched.unset_timeout(&timers[4]);
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_ChronoWrapper_Chrono_Running::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_ChronoWrapper_Chrono_Running::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_ChronoWrapper_Chrono_Running::enter_actions(timers, data, internal, sched, output);
  }
}

// Or-state
#[derive(Copy, Clone)]
enum State_P_ChronoWrapper_Chrono {
  S_Stopped(State_P_ChronoWrapper_Chrono_Stopped),
  S_Running(State_P_ChronoWrapper_Chrono_Running),
}
impl Default for State_P_ChronoWrapper_Chrono {
  fn default() -> Self {
    Self::S_Stopped(Default::default())
  }
}
impl State_P_ChronoWrapper_Chrono {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_ChronoWrapper_Chrono::enter_actions(timers, data, internal, sched, output);
    State_P_ChronoWrapper_Chrono_Stopped::enter_default(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    match self {
      Self::S_Stopped(s) => { s.exit_current(timers, data, internal, sched, output); },
      Self::S_Running(s) => { s.exit_current(timers, data, internal, sched, output); },
    }
    State_P_ChronoWrapper_Chrono::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_ChronoWrapper_Chrono::enter_actions(timers, data, internal, sched, output);
    match self {
      Self::S_Stopped(s) => { s.enter_current(timers, data, internal, sched, output); },
      Self::S_Running(s) => { s.enter_current(timers, data, internal, sched, output); },
    }
  }
}

// Or-state
#[derive(Copy, Clone)]
enum State_P_ChronoWrapper {
  S_Chrono(State_P_ChronoWrapper_Chrono),
}
impl Default for State_P_ChronoWrapper {
  fn default() -> Self {
    Self::S_Chrono(Default::default())
  }
}
impl State_P_ChronoWrapper {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_ChronoWrapper::enter_actions(timers, data, internal, sched, output);
    State_P_ChronoWrapper_Chrono::enter_default(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    match self {
      Self::S_Chrono(s) => { s.exit_current(timers, data, internal, sched, output); },
    }
    State_P_ChronoWrapper::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_ChronoWrapper::enter_actions(timers, data, internal, sched, output);
    match self {
      Self::S_Chrono(s) => { s.enter_current(timers, data, internal, sched, output); },
    }
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_Display_TimeUpdate {
}
impl State_P_Display_TimeUpdate {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    (output)(OutEvent::E_refreshTimeDisplay);
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_TimeUpdate::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_TimeUpdate::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_TimeUpdate::enter_actions(timers, data, internal, sched, output);
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_Display_WaitingToEdit {
}
impl State_P_Display_WaitingToEdit {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    timers[5] = sched.set_timeout(1500, InEvent::A5);
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    sched.unset_timeout(&timers[5]);
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_WaitingToEdit::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_WaitingToEdit::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_WaitingToEdit::enter_actions(timers, data, internal, sched, output);
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_Display_WaitingForAlarm {
}
impl State_P_Display_WaitingForAlarm {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    (output)(OutEvent::E_refreshAlarmDisplay);
    timers[6] = sched.set_timeout(1500, InEvent::A6);
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    sched.unset_timeout(&timers[6]);
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_WaitingForAlarm::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_WaitingForAlarm::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_WaitingForAlarm::enter_actions(timers, data, internal, sched, output);
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_Display_EditingTime_Waiting {
}
impl State_P_Display_EditingTime_Waiting {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    timers[7] = sched.set_timeout(5000, InEvent::A7);
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    sched.unset_timeout(&timers[7]);
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_EditingTime_Waiting::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_EditingTime_Waiting::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_EditingTime_Waiting::enter_actions(timers, data, internal, sched, output);
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_Display_EditingTime_GoingToNext {
}
impl State_P_Display_EditingTime_GoingToNext {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    timers[8] = sched.set_timeout(2000, InEvent::A8);
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    sched.unset_timeout(&timers[8]);
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_EditingTime_GoingToNext::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_EditingTime_GoingToNext::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_EditingTime_GoingToNext::enter_actions(timers, data, internal, sched, output);
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_Display_EditingTime_Increasing {
}
impl State_P_Display_EditingTime_Increasing {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    (output)(OutEvent::E_increaseSelection);
    timers[9] = sched.set_timeout(300, InEvent::A9);
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    sched.unset_timeout(&timers[9]);
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_EditingTime_Increasing::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_EditingTime_Increasing::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_EditingTime_Increasing::enter_actions(timers, data, internal, sched, output);
  }
}

// Or-state
#[derive(Copy, Clone)]
enum State_P_Display_EditingTime {
  S_Waiting(State_P_Display_EditingTime_Waiting),
  S_GoingToNext(State_P_Display_EditingTime_GoingToNext),
  S_Increasing(State_P_Display_EditingTime_Increasing),
}
impl Default for State_P_Display_EditingTime {
  fn default() -> Self {
    Self::S_Waiting(Default::default())
  }
}
impl State_P_Display_EditingTime {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    (output)(OutEvent::E_startSelection);
    internal.raise().e_time_edit = Some(Event_time_edit{});
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    (output)(OutEvent::E_stopSelection);
    internal.raise().e_edit_done = Some(Event_edit_done{});
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_EditingTime::enter_actions(timers, data, internal, sched, output);
    State_P_Display_EditingTime_Waiting::enter_default(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    match self {
      Self::S_Waiting(s) => { s.exit_current(timers, data, internal, sched, output); },
      Self::S_GoingToNext(s) => { s.exit_current(timers, data, internal, sched, output); },
      Self::S_Increasing(s) => { s.exit_current(timers, data, internal, sched, output); },
    }
    State_P_Display_EditingTime::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_EditingTime::enter_actions(timers, data, internal, sched, output);
    match self {
      Self::S_Waiting(s) => { s.enter_current(timers, data, internal, sched, output); },
      Self::S_GoingToNext(s) => { s.enter_current(timers, data, internal, sched, output); },
      Self::S_Increasing(s) => { s.enter_current(timers, data, internal, sched, output); },
    }
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_Display_ChronoUpdate {
}
impl State_P_Display_ChronoUpdate {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    (output)(OutEvent::E_refreshChronoDisplay);
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_ChronoUpdate::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_ChronoUpdate::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display_ChronoUpdate::enter_actions(timers, data, internal, sched, output);
  }
}

// Or-state
#[derive(Copy, Clone)]
enum State_P_Display {
  S_TimeUpdate(State_P_Display_TimeUpdate),
  S_WaitingToEdit(State_P_Display_WaitingToEdit),
  S_WaitingForAlarm(State_P_Display_WaitingForAlarm),
  S_EditingTime(State_P_Display_EditingTime),
  S_ChronoUpdate(State_P_Display_ChronoUpdate),
}
impl Default for State_P_Display {
  fn default() -> Self {
    Self::S_TimeUpdate(Default::default())
  }
}
impl State_P_Display {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display::enter_actions(timers, data, internal, sched, output);
    State_P_Display_TimeUpdate::enter_default(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    match self {
      Self::S_TimeUpdate(s) => { s.exit_current(timers, data, internal, sched, output); },
      Self::S_WaitingToEdit(s) => { s.exit_current(timers, data, internal, sched, output); },
      Self::S_WaitingForAlarm(s) => { s.exit_current(timers, data, internal, sched, output); },
      Self::S_EditingTime(s) => { s.exit_current(timers, data, internal, sched, output); },
      Self::S_ChronoUpdate(s) => { s.exit_current(timers, data, internal, sched, output); },
    }
    State_P_Display::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Display::enter_actions(timers, data, internal, sched, output);
    match self {
      Self::S_TimeUpdate(s) => { s.enter_current(timers, data, internal, sched, output); },
      Self::S_WaitingToEdit(s) => { s.enter_current(timers, data, internal, sched, output); },
      Self::S_WaitingForAlarm(s) => { s.enter_current(timers, data, internal, sched, output); },
      Self::S_EditingTime(s) => { s.enter_current(timers, data, internal, sched, output); },
      Self::S_ChronoUpdate(s) => { s.enter_current(timers, data, internal, sched, output); },
    }
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_Time_Increasing {
}
impl State_P_Time_Increasing {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    timers[10] = sched.set_timeout(1000, InEvent::A10);
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
    sched.unset_timeout(&timers[10]);
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Time_Increasing::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Time_Increasing::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Time_Increasing::enter_actions(timers, data, internal, sched, output);
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P_Time_Editing {
}
impl State_P_Time_Editing {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Time_Editing::enter_actions(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Time_Editing::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Time_Editing::enter_actions(timers, data, internal, sched, output);
  }
}

// Or-state
#[derive(Copy, Clone)]
enum State_P_Time {
  S_Increasing(State_P_Time_Increasing),
  S_Editing(State_P_Time_Editing),
}
impl Default for State_P_Time {
  fn default() -> Self {
    Self::S_Increasing(Default::default())
  }
}
impl State_P_Time {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Time::enter_actions(timers, data, internal, sched, output);
    State_P_Time_Increasing::enter_default(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    match self {
      Self::S_Increasing(s) => { s.exit_current(timers, data, internal, sched, output); },
      Self::S_Editing(s) => { s.exit_current(timers, data, internal, sched, output); },
    }
    State_P_Time::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P_Time::enter_actions(timers, data, internal, sched, output);
    match self {
      Self::S_Increasing(s) => { s.enter_current(timers, data, internal, sched, output); },
      Self::S_Editing(s) => { s.enter_current(timers, data, internal, sched, output); },
    }
  }
}

// And-state
#[derive(Default, Copy, Clone)]
struct State_P {
  s_P_Alarm: State_P_Alarm,
  s_P_Indiglo: State_P_Indiglo,
  s_P_ChronoWrapper: State_P_ChronoWrapper,
  s_P_Display: State_P_Display,
  s_P_Time: State_P_Time,
}
impl State_P {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P::enter_actions(timers, data, internal, sched, output);
    State_P_Alarm::enter_default(timers, data, internal, sched, output);
    State_P_Indiglo::enter_default(timers, data, internal, sched, output);
    State_P_ChronoWrapper::enter_default(timers, data, internal, sched, output);
    State_P_Display::enter_default(timers, data, internal, sched, output);
    State_P_Time::enter_default(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    self.s_P_Alarm.exit_current(timers, data, internal, sched, output);
    self.s_P_Indiglo.exit_current(timers, data, internal, sched, output);
    self.s_P_ChronoWrapper.exit_current(timers, data, internal, sched, output);
    self.s_P_Display.exit_current(timers, data, internal, sched, output);
    self.s_P_Time.exit_current(timers, data, internal, sched, output);
    State_P::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    State_P::enter_actions(timers, data, internal, sched, output);
    self.s_P_Alarm.enter_current(timers, data, internal, sched, output);
    self.s_P_Indiglo.enter_current(timers, data, internal, sched, output);
    self.s_P_ChronoWrapper.enter_current(timers, data, internal, sched, output);
    self.s_P_Display.enter_current(timers, data, internal, sched, output);
    self.s_P_Time.enter_current(timers, data, internal, sched, output);
  }
}

// Or-state
#[derive(Copy, Clone)]
enum Root {
  S_P(State_P),
}
impl Default for Root {
  fn default() -> Self {
    Self::S_P(Default::default())
  }
}
impl Root {
  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    let scope = data;
  }
  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    Root::enter_actions(timers, data, internal, sched, output);
    State_P::enter_default(timers, data, internal, sched, output);
  }
  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    match self {
      Self::S_P(s) => { s.exit_current(timers, data, internal, sched, output); },
    }
    Root::exit_actions(timers, data, internal, sched, output);
  }
  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {
    Root::enter_actions(timers, data, internal, sched, output);
    match self {
      Self::S_P(s) => { s.enter_current(timers, data, internal, sched, output); },
    }
  }
}

fn f0_guard(builtin_conf: (State_P_Indiglo, State_P_ChronoWrapper, State_P_Display, State_P_Time, ), ) -> bool {
  let scope = action_lang::Empty{};
  let mut scope = Scope0_guard_l1 {
    _base: scope,
    builtin_conf,
  };
  return { // macro expansion for @in("/P/Display/TimeUpdate")
    let (ref s_P_Indiglo, ref s_P_ChronoWrapper, ref s_P_Display, ref s_P_Time, ) = scope.builtin_conf;
    if let State_P_Display::S_TimeUpdate(ref s_P_Display_TimeUpdate) = s_P_Display {
      true
    } else { false }
  };
}

fn f1_guard(builtin_conf: (State_P_Indiglo, State_P_ChronoWrapper, State_P_Display, State_P_Time, ), ) -> bool {
  let scope = action_lang::Empty{};
  let mut scope = Scope1_guard_l1 {
    _base: scope,
    builtin_conf,
  };
  return { // macro expansion for @in("/P/Display/TimeUpdate")
    let (ref s_P_Indiglo, ref s_P_ChronoWrapper, ref s_P_Display, ref s_P_Time, ) = scope.builtin_conf;
    if let State_P_Display::S_TimeUpdate(ref s_P_Display_TimeUpdate) = s_P_Display {
      true
    } else { false }
  };
}

fn f2_guard(builtin_conf: (State_P_Alarm, State_P_Indiglo, State_P_Display, State_P_Time, ), ) -> bool {
  let scope = action_lang::Empty{};
  let mut scope = Scope2_guard_l1 {
    _base: scope,
    builtin_conf,
  };
  return { // macro expansion for @in("/P/Display/ChronoUpdate")
    let (ref s_P_Alarm, ref s_P_Indiglo, ref s_P_Display, ref s_P_Time, ) = scope.builtin_conf;
    if let State_P_Display::S_ChronoUpdate(ref s_P_Display_ChronoUpdate) = s_P_Display {
      true
    } else { false }
  };
}

fn f3_guard(builtin_conf: (State_P_Alarm, State_P_Indiglo, State_P_Display, State_P_Time, ), ) -> bool {
  let scope = action_lang::Empty{};
  let mut scope = Scope3_guard_l1 {
    _base: scope,
    builtin_conf,
  };
  return { // macro expansion for @in("/P/Display/ChronoUpdate")
    let (ref s_P_Alarm, ref s_P_Indiglo, ref s_P_Display, ref s_P_Time, ) = scope.builtin_conf;
    if let State_P_Display::S_ChronoUpdate(ref s_P_Display_ChronoUpdate) = s_P_Display {
      true
    } else { false }
  };
}

fn f4_guard(builtin_conf: (State_P_Alarm, State_P_Indiglo, State_P_Display, State_P_Time, ), ) -> bool {
  let scope = action_lang::Empty{};
  let mut scope = Scope4_guard_l1 {
    _base: scope,
    builtin_conf,
  };
  return { // macro expansion for @in("/P/Display/ChronoUpdate")
    let (ref s_P_Alarm, ref s_P_Indiglo, ref s_P_Display, ref s_P_Time, ) = scope.builtin_conf;
    if let State_P_Display::S_ChronoUpdate(ref s_P_Display_ChronoUpdate) = s_P_Display {
      true
    } else { false }
  };
}

inherit_struct! {
  Scope0_guard_l1 (action_lang::Empty) {
    builtin_conf: (State_P_Indiglo, State_P_ChronoWrapper, State_P_Display, State_P_Time, ),
  }
}

inherit_struct! {
  Scope1_guard_l1 (action_lang::Empty) {
    builtin_conf: (State_P_Indiglo, State_P_ChronoWrapper, State_P_Display, State_P_Time, ),
  }
}

inherit_struct! {
  Scope2_guard_l1 (action_lang::Empty) {
    builtin_conf: (State_P_Alarm, State_P_Indiglo, State_P_Display, State_P_Time, ),
  }
}

inherit_struct! {
  Scope3_guard_l1 (action_lang::Empty) {
    builtin_conf: (State_P_Alarm, State_P_Indiglo, State_P_Display, State_P_Time, ),
  }
}

inherit_struct! {
  Scope4_guard_l1 (action_lang::Empty) {
    builtin_conf: (State_P_Alarm, State_P_Indiglo, State_P_Display, State_P_Time, ),
  }
}

