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
        # By default, if the parent of a history state has never been exited before, the parent's default states should be entered.
        self.history_values: List[Bitmap] = [h.parent.opt.ts_static for h in statechart.tree.history_states]

        # Scheduled IDs for after triggers
        self.timer_ids = [None] * len(statechart.tree.after_triggers)

    # enter default states
    def initialize(self):
        states = self.statechart.tree.root.opt.ts_static
        self.configuration = states

        ctx = EvalContext(execution=self, events=[], memory=self.rhs_memory)
        if self.statechart.datamodel is not None:
            self.statechart.datamodel.exec(self.rhs_memory)

        for state in self._ids_to_states(bm_items(states)):
            print_debug(termcolor.colored('  ENTER %s'%state.opt.full_name, 'green'))
            self._perform_actions(ctx, state.enter)
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
                    enter_ids = t.opt.enter_states_static | reduce(lambda x,y: x|y, (self.history_values[s.history_id] for s in t.opt.enter_states_dynamic), Bitmap())
                    enter_set = self._ids_to_states(bm_items(enter_ids))

                ctx = EvalContext(execution=self, events=events, memory=self.rhs_memory)

                print_debug("fire " + str(t))

                with timer.Context("exit states"):
                    # exit states...
                    for s in exit_set:
                        print_debug(termcolor.colored('  EXIT %s' % s.opt.full_name, 'green'))
                        # remember which state(s) we were in if a history state is present
                        for h, mask in s.opt.history:
                            self.history_values[h.history_id] = exit_ids & mask
                        self._cancel_timers(s.opt.after_triggers)
                        self._perform_actions(ctx, s.exit)
                        self.configuration &= ~s.opt.state_id_bitmap

                # execute transition action(s)
                with timer.Context("actions"):
                    self.rhs_memory.push_frame(t.scope) # make room for event parameters on stack
                    if t.trigger:
                        t.trigger.copy_params_to_stack(ctx)
                    self._perform_actions(ctx, t.actions)
                    self.rhs_memory.pop_frame()

                with timer.Context("enter states"):
                    # enter states...
                    for s in enter_set:
                        print_debug(termcolor.colored('  ENTER %s' % s.opt.full_name, 'green'))
                        self.configuration |= s.opt.state_id_bitmap
                        self._perform_actions(ctx, s.enter)
                        self._start_timers(s.opt.after_triggers)

                self.rhs_memory.flush_transition()

            # input(">")

        except SCCDRuntimeException as e:
            e.args = ("During execution of transition %s:\n" % str(t) +str(e),)
            raise

    def check_guard(self, t, events) -> bool:
        try:
            if t.guard is None:
                return True
            else:
                ctx = EvalContext(execution=self, events=events, memory=self.gc_memory)
                self.gc_memory.push_frame(t.scope)
                # Guard conditions can also refer to event parameters
                if t.trigger:
                    t.trigger.copy_params_to_stack(ctx)
                result = t.guard.eval(self.gc_memory)
                self.gc_memory.pop_frame()
                return result
        except SCCDRuntimeException as e:
            e.args = ("While checking guard of transition %s:\n" % str(t) +str(e),)
            raise

    def check_source(self, t) -> bool:
        return self.configuration & t.source.opt.state_id_bitmap

    @staticmethod
    def _perform_actions(ctx: EvalContext, actions: List[Action]):
        for a in actions:
            a.exec(ctx)

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
        state_ids_bitmap = states_to_bitmap((self.statechart.tree.state_dict[state_string] for state_string in state_strings))
        in_state = bm_has_all(self.configuration, state_ids_bitmap)
        # if in_state:
        #     print_debug("in state"+str(state_strings))
        # else:
        #     print_debug("not in state"+str(state_strings))
        return in_state
