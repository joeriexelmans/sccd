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

    def __init__(self, statechart: Statechart, instance):
        self.statechart = statechart
        self.instance = instance

        self.gc_memory = None
        self.rhs_memory = None
        self.raise_internal = None
        self.raise_next_bs = None

        # these 2 fields have the same information
        self.configuration: List[State] = []
        self.configuration_bitmap: Bitmap = Bitmap()

        self.eventless_states = 0 # number of states in current configuration that have at least one eventless outgoing transition.

        # mapping from configuration_bitmap (=int) to configuration (=List[State])
        self.config_mem = {}
        # mapping from history state id to states to enter if history is target of transition
        self.history_values: Dict[int, List[State]] = {}

        # For each AfterTrigger in the statechart tree, we keep an expected 'id' that is
        # a parameter to a future 'after' event. This 'id' is incremented each time a timer
        # is started, so we only respond to the most recent one.
        self.timer_ids = [-1] * len(statechart.tree.after_triggers)

        # output events accumulate here until they are collected
        self.output = []

    # enter default states
    def initialize(self):
        states = self.statechart.tree.root.target_states(self, True)
        self.configuration.extend(self.statechart.tree.state_list[id] for id in states.items())
        self.configuration_bitmap = states

        ctx = EvalContext(current_state=self, events=[], memory=self.rhs_memory)
        if self.statechart.datamodel is not None:
            self.statechart.datamodel.exec(self.rhs_memory)

        for state in self.configuration:
            print_debug(termcolor.colored('  ENTER %s'%state.gen.full_name, 'green'))
            self.eventless_states += state.gen.has_eventless_transitions
            self._perform_actions(ctx, state.enter)
            self._start_timers(state.gen.after_triggers)

        self.rhs_memory.flush_transition()
        self.rhs_memory.flush_round()
        self.gc_memory.flush_round()

    # events: list SORTED by event id
    def fire_transition(self, events: List[Event], t: Transition):
        try:
            timer.start("transition")

            timer.start("exit states")
            # Exit set is the intersection between self.configuration and t.gen.arena.descendants.

            # The following was found to have better performance than reverse-iterating and filtering self.configuration or t.arena.gen.descendants lists, despite the fact that Bitmap.reverse_items() isn't very efficient.
            exit_ids = self.configuration_bitmap & t.gen.arena.gen.descendants_bitmap
            exit_set = (self.statechart.tree.state_list[id] for id in exit_ids.reverse_items())

            # Alternative implementation:
            # if len(self.configuration) < len(t.gen.arena.gen.descendants):
            #     exit_set = (s for s in self.configuration if s.gen.state_id_bitmap & t.gen.arena.gen.descendants_bitmap)
            # else:
            #     exit_set = (s for s in t.gen.arena.gen.descendants if s.gen.state_id_bitmap & self.configuration_bitmap)
            timer.stop("exit states")


            timer.start("enter states")
            # Enter path is the intersection between:
            #   1) the transitions target + the target's ancestors and
            #   2) the arena's descendants
            enter_path = (t.targets[0].gen.ancestors_bitmap | t.targets[0].gen.state_id_bitmap) & t.gen.arena.gen.descendants_bitmap
            # Now, along the enter path, there may be AND-states whose children we don't explicitly enter, but should enter.
            # That's why we call 'target_states' on every state on the path and join the results.
            items = enter_path.items()
            shifted = itertools.chain(enter_path.items(), [-1])
            next(shifted) # throw away first value
            pairwise = zip(items, shifted)

            enter_ids = Bitmap()
            for state_id, next_state_id in pairwise:
                enter_ids |= self.statechart.tree.state_list[state_id].target_states(self, next_state_id == -1)
            enter_set = (self.statechart.tree.state_list[id] for id in enter_ids.items())
            timer.stop("enter states")


            ctx = EvalContext(current_state=self, events=events, memory=self.rhs_memory)

            print_debug("fire " + str(t))

            timer.start("exit states")
            # exit states...
            for s in exit_set:
                # remember which state(s) we were in if a history state is present
                for h in s.gen.history:
                    if isinstance(h, DeepHistoryState):
                        f = lambda s0: not s0.gen.descendants_bitmap and s0.gen.state_id_bitmap & s.gen.descendants_bitmap
                    else:
                        f = lambda s0: s0.gen.ancestors_bitmap and s0.parent == s
                    self.history_values[h.gen.state_id] = list(filter(f, self.configuration))

                print_debug(termcolor.colored('  EXIT %s' % s.gen.full_name, 'green'))
                self.eventless_states -= s.gen.has_eventless_transitions
                # execute exit action(s)
                self._perform_actions(ctx, s.exit)
                # self.rhs_memory.pop_local_scope(s.scope)
                self.configuration_bitmap &= ~s.gen.state_id_bitmap
            timer.stop("exit states")

            # execute transition action(s)
            timer.start("actions")
            self.rhs_memory.push_frame(t.scope) # make room for event parameters on stack
            if t.trigger:
                t.trigger.copy_params_to_stack(ctx)
            self._perform_actions(ctx, t.actions)
            self.rhs_memory.pop_frame()
            timer.stop("actions")

            timer.start("enter states")
            # enter states...
            for s in enter_set:
                print_debug(termcolor.colored('  ENTER %s' % s.gen.full_name, 'green'))
                self.eventless_states += s.gen.has_eventless_transitions
                self.configuration_bitmap |= s.gen.state_id_bitmap
                # execute enter action(s)
                self._perform_actions(ctx, s.enter)
                self._start_timers(s.gen.after_triggers)
            timer.stop("enter states")
            
            try:
                self.configuration = self.config_mem[self.configuration_bitmap]
            except KeyError:
                self.configuration = self.config_mem[self.configuration_bitmap] = [s for s in self.statechart.tree.state_list if self.configuration_bitmap & s.gen.state_id_bitmap]

            self.rhs_memory.flush_transition()

            timer.stop("transition")

        except SCCDRuntimeException as e:
            e.args = ("During execution of transition %s:\n" % str(t) +str(e),)
            raise

    def check_guard(self, t, events) -> bool:
        try:
            # Special case: after trigger
            if isinstance(t.trigger, AfterTrigger):
                e = [e for e in events if bit(e.id) & t.trigger.enabling_bitmap][0] # it's safe to assume the list will contain one element cause we only check a transition's guard after we know it may be enabled given the set of events
                if self.timer_ids[t.trigger.after_id] != e.params[0]:
                    return False

            if t.guard is None:
                return True
            else:
                ctx = EvalContext(current_state=self, events=events, memory=self.gc_memory)
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
        return self.configuration_bitmap & t.source.gen.state_id_bitmap

    @staticmethod
    def _perform_actions(ctx: EvalContext, actions: List[Action]):
        for a in actions:
            a.exec(ctx)

    def _start_timers(self, triggers: List[AfterTrigger]):
        for after in triggers:
            delay: Duration = after.delay.eval(
                EvalContext(current_state=self, events=[], memory=self.gc_memory))
            timer_id = self._next_timer_id(after)
            self.raise_next_bs(Event(id=after.id, name=after.name, params=[timer_id]), delay)

    def _next_timer_id(self, trigger: AfterTrigger):
        self.timer_ids[trigger.after_id] += 1
        return self.timer_ids[trigger.after_id]

    # Return whether the current configuration includes ALL the states given.
    def in_state(self, state_strings: List[str]) -> bool:
        state_ids_bitmap = Bitmap.from_list((self.statechart.tree.state_dict[state_string].gen.state_id for state_string in state_strings))
        in_state = self.configuration_bitmap.has_all(state_ids_bitmap)
        # if in_state:
        #     print_debug("in state"+str(state_strings))
        # else:
        #     print_debug("not in state"+str(state_strings))
        return in_state

    def collect_output(self) -> List[OutputEvent]:
        output = self.output
        self.output = []
        return output
