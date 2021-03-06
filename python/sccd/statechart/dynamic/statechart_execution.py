from typing import *
from sccd.statechart.static.statechart import *
from sccd.statechart.dynamic.event import *
from sccd.util.debug import print_debug
from sccd.util.bitmap import *
from sccd.action_lang.static.scope import *
from sccd.common.exceptions import *
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
        self.timer_ids = [None] * statechart.tree.timer_count

    # enter default states
    def initialize(self):
        self.configuration = self.statechart.tree.initial_states

        if self.statechart.datamodel is not None:
            self.statechart.datamodel.exec(self.rhs_memory)

        ctx = EvalContext(memory=self.rhs_memory, execution=self, params=[])

        for state in self.statechart.tree.bitmap_to_states(self.configuration):
            print_debug(termcolor.colored('  ENTER %s'%state.full_name, 'green'))
            _perform_actions(ctx, state.enter)
            self._start_timers(state.after_triggers)

        self.rhs_memory.flush_transition()
        self.rhs_memory.flush_round()
        self.gc_memory.flush_round()

    # events: list SORTED by event id
    def fire_transition(self, events: List[InternalEvent], t: Transition):
        try:
            with timer.Context("transition"):
                # Sequence of exit states is the intersection between set of current states and the arena's descendants.
                with timer.Context("exit set"):
                    exit_ids = self.configuration & t.exit_mask
                    exit_set = self.statechart.tree.bitmap_to_states_reverse(exit_ids)

                with timer.Context("enter set"):
                    # Sequence of enter states is more complex but has for a large part already been computed statically.
                    enter_ids = t.enter_states_static
                    if t.target_history_id is not None:
                        enter_ids |= self.history_values[t.target_history_id]
                    enter_set = self.statechart.tree.bitmap_to_states(enter_ids)

                ctx = EvalContext(memory=self.rhs_memory, execution=self, params=get_event_params(events, t.trigger))

                print_debug("fire " + str(t))

                with timer.Context("exit states"):
                    just_exited = None
                    for s in exit_set:
                        print_debug(termcolor.colored('  EXIT %s' % s.full_name, 'green'))
                        if s.deep_history is not None:
                            # s has a deep-history child:
                            history_id, history_mask, _ = s.deep_history
                            self.history_values[history_id] = exit_ids & history_mask
                        if s.shallow_history is not None:
                            history_id, _ = s.shallow_history
                            self.history_values[history_id] = just_exited.effective_targets
                        self._cancel_timers(s.after_triggers)
                        _perform_actions(ctx, s.exit)
                        self.configuration &= ~s.state_id_bitmap
                        just_exited = s

                # execute transition action(s)
                with timer.Context("actions"):
                    _perform_actions(ctx, t.actions)

                with timer.Context("enter states"):
                    for s in enter_set:
                        print_debug(termcolor.colored('  ENTER %s' % s.full_name, 'green'))
                        self.configuration |= s.state_id_bitmap
                        _perform_actions(ctx, s.enter)
                        self._start_timers(s.after_triggers)

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
                result = t.guard.eval(self.gc_memory)(self.gc_memory, self.configuration, *get_event_params(events, t.trigger))
                return result
        except Exception as e:
            e.args = ("While checking guard of transition %s:\n" % str(t) + str(e),)
            raise

    def _start_timers(self, triggers: List[AfterTrigger]):
        for after in triggers:
            delay: Duration = after.delay.eval(
                EvalContext(memory=self.gc_memory, execution=self, params=[]))
            self.timer_ids[after.after_id] = self.schedule_callback(delay, InternalEvent(name=after.name, params=[]), [self.instance])

    def _cancel_timers(self, triggers: List[AfterTrigger]):
        for after in triggers:
            if self.timer_ids[after.after_id] is not None:
                self.cancel_callback(self.timer_ids[after.after_id])
                self.timer_ids[after.after_id] = None
                

def _perform_actions(ctx: EvalContext, actions: List[Action]):
    for a in actions:
        a.exec(ctx)


def get_event_params(events: List[InternalEvent], trigger) -> List[any]:
    params = []
    for e in trigger.enabling:
        for f in events:
            if e.name == f.name:
                params.extend(f.params)
    return params
