from typing import *
from sccd.statechart.static.statechart import *
from sccd.statechart.dynamic.event import *
from sccd.util.debug import print_debug
from sccd.util.bitmap import *
from sccd.action_lang.static.scope import *
from sccd.action_lang.dynamic.exceptions import *
from sccd.util import timer

# Set of current states etc.
class StatechartExecution:
    __slots__ = ["instance", "statechart", "gc_memory", "rhs_memory", "raise_internal", "raise_output", "configuration", "history_values", "timer_ids", "schedule_callback", "cancel_callback"]

    def __init__(self, instance, statechart: Statechart):
        self.instance = instance
        self.statechart = statechart

        self.gc_memory = None
        self.rhs_memory = None
        self.raise_internal = None
        self.raise_output = None

        # set of current states
        self.configuration: Bitmap = Bitmap()

        # Mapping from history_id to set of states to enter if history is target of transition
        self.history_values: List[Bitmap] = list(statechart.tree.initial_history_values)

        # Scheduled IDs for after triggers
        self.timer_ids = [None] * len(statechart.tree.after_triggers)

    # enter default states
    def initialize(self):
        self.configuration = self.statechart.tree.initial_states

        ctx = EvalContext(execution=self, events=[], memory=self.rhs_memory)
        if self.statechart.datamodel is not None:
            self.statechart.datamodel.exec(self.rhs_memory)

        for state in self._ids_to_states(bm_items(self.configuration)):
            print_debug(termcolor.colored('  ENTER %s'%state.opt.full_name, 'green'))
            _perform_actions(ctx, state.enter)
            self._start_timers(state.opt.after_triggers)

        self.rhs_memory.flush_transition()
        self.rhs_memory.flush_round()
        self.gc_memory.flush_round()

    def _ids_to_states(self, id_iter):
        return (self.statechart.tree.state_list[id] for id in id_iter)

    # events: list SORTED by event id
    def fire_transition(self, events: List[InternalEvent], t: Transition):
        try:
            with timer.Context("transition"):
                # Sequence of exit states is the intersection between set of current states and the arena's descendants.
                with timer.Context("exit set"):
                    exit_ids = self.configuration & t.opt.arena.opt.descendants
                    exit_set = self._ids_to_states(bm_reverse_items(exit_ids))

                with timer.Context("enter set"):
                    # Sequence of enter states is more complex but has for a large part already been computed statically.
                    enter_ids = t.opt.enter_states_static
                    if t.opt.target_history_id is not None:
                        enter_ids |= self.history_values[t.opt.target_history_id]
                    enter_set = self._ids_to_states(bm_items(enter_ids))

                self.rhs_memory.set_read_only(False)
                ctx = EvalContext(execution=self, events=events, memory=self.rhs_memory)

                print_debug("fire " + str(t))

                with timer.Context("exit states"):
                    just_exited = None
                    for s in exit_set:
                        print_debug(termcolor.colored('  EXIT %s' % s.opt.full_name, 'green'))
                        if s.opt.deep_history is not None:
                            # s has a deep-history child:
                            history_id, history_mask = s.opt.deep_history
                            self.history_values[history_id] = exit_ids & history_mask
                        if s.opt.shallow_history is not None:
                            history_id = s.opt.shallow_history
                            self.history_values[history_id] = just_exited.opt.effective_targets
                        self._cancel_timers(s.opt.after_triggers)
                        _perform_actions(ctx, s.exit)
                        self.configuration &= ~s.opt.state_id_bitmap
                        just_exited = s

                # execute transition action(s)
                with timer.Context("actions"):
                    self.rhs_memory.push_frame(t.scope) # make room for event parameters on stack
                    if t.trigger:
                        t.trigger.copy_params_to_stack(events, self.rhs_memory)
                    _perform_actions(ctx, t.actions)
                    self.rhs_memory.pop_frame()

                with timer.Context("enter states"):
                    for s in enter_set:
                        print_debug(termcolor.colored('  ENTER %s' % s.opt.full_name, 'green'))
                        self.configuration |= s.opt.state_id_bitmap
                        _perform_actions(ctx, s.enter)
                        self._start_timers(s.opt.after_triggers)

                self.rhs_memory.flush_transition()

            # input(">")

        except Exception as e:
            e.args = ("During execution of transition %s:\n" % str(t) +str(e),)
            raise

    def check_guard(self, t: Transition, events: List[InternalEvent]) -> bool:
        try:
            if t.guard is None:
                return True
            else:
                self.gc_memory.set_read_only(True)
                self.gc_memory.push_frame(t.scope)
                # Guard conditions can also refer to event parameters
                if t.trigger:
                    t.trigger.copy_params_to_stack(events, self.gc_memory)
                result = t.guard.eval(self.gc_memory)
                self.gc_memory.pop_frame()
                return result
        except Exception as e:
            e.args = ("While checking guard of transition %s:\n" % str(t) + str(e),)
            raise

    def _start_timers(self, triggers: List[AfterTrigger]):
        for after in triggers:
            delay: Duration = after.delay.eval(
                EvalContext(execution=self, events=[], memory=self.gc_memory))
            self.timer_ids[after.after_id] = self.schedule_callback(delay, InternalEvent(id=after.id, name=after.name, params=[]), [self.instance])

    def _cancel_timers(self, triggers: List[AfterTrigger]):
        for after in triggers:
            if self.timer_ids[after.after_id] is not None:
                self.cancel_callback(self.timer_ids[after.after_id])
                self.timer_ids[after.after_id] = None

    # Return whether the current configuration includes ALL the states given.
    def in_state(self, state_strings: List[str]) -> bool:
        try:
            state_ids_bitmap = bm_union(self.statechart.tree.state_dict[state_string].opt.state_id_bitmap for state_string in state_strings)
        except KeyError as e:
            raise SCCDRuntimeException("INSTATE argument %s: invalid state" % str(e)) from e
        in_state = bm_has_all(self.configuration, state_ids_bitmap)
        # if in_state:
        #     print_debug("in state"+str(state_strings))
        # else:
        #     print_debug("not in state"+str(state_strings))
        return in_state


def _perform_actions(ctx: EvalContext, actions: List[Action]):
    for a in actions:
        a.exec(ctx)
