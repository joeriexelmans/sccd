from typing import *
from sccd.syntax.statechart import *
from sccd.execution.event import *
from sccd.util.debug import print_debug
from sccd.util.bitmap import *
from sccd.syntax.scope import *


# Set of current states etc.
class StatechartState:

    def __init__(self, statechart: Statechart, instance, gc_memory, rhs_memory, raise_internal):
        self.model = statechart
        self.instance = instance
        self.gc_memory = gc_memory
        self.rhs_memory = rhs_memory
        self.raise_internal = raise_internal

        # these 2 fields have the same information
        self.configuration: List[State] = []
        self.configuration_bitmap: Bitmap = Bitmap()

        self.eventless_states = 0 # number of states in current configuration that have at least one eventless outgoing transition.

        # mapping from configuration_bitmap (=int) to configuration (=List[State])
        self.config_mem = {}
        # mapping from history state id to states to enter if history is target of transition
        self.history_values = {}

        # For each AfterTrigger in the statechart tree, we keep an expected 'id' that is
        # a parameter to a future 'after' event. This 'id' is incremented each time a timer
        # is started, so we only respond to the most recent one.
        self.timer_ids = [-1] * len(statechart.tree.after_triggers)

        # output events accumulate here until they are collected
        self.output = []

    # enter default states
    def initialize(self):
        states = self.model.tree.root.getEffectiveTargetStates(self)
        self.configuration.extend(states)
        self.configuration_bitmap = Bitmap.from_list(s.gen.state_id for s in states)

        ctx = EvalContext(current_state=self, events=[], memory=self.rhs_memory)
        if self.model.datamodel is not None:
            self.model.datamodel.exec(ctx)

        for state in states:
            print_debug(termcolor.colored('  ENTER %s'%state.gen.full_name, 'green'))
            self.eventless_states += state.gen.has_eventless_transitions
            self._perform_actions(ctx, state.enter)
            self._start_timers(state.gen.after_triggers)

        self.rhs_memory.flush_transition()
        self.rhs_memory.flush_round()

    # events: list SORTED by event id
    def fire_transition(self, events: List[Event], t: Transition):
        def __exitSet():
            return [s for s in reversed(t.gen.lca.gen.descendants) if (s in self.configuration)]
        
        def __enterSet(targets):
            target = targets[0]
            for a in reversed(target.gen.ancestors):
                if a in t.source.gen.ancestors:
                    continue
                else:
                    yield a
            for target in targets:
                yield target

        def __getEffectiveTargetStates():
            targets = []
            for target in t.targets:
                for e_t in target.getEffectiveTargetStates(self):
                    if not e_t in targets:
                        targets.append(e_t)
            return targets

        # exit states...
        exit_set = __exitSet()
        for s in exit_set:
            # remember which state(s) we were in if a history state is present
            for h in s.gen.history:
                f = lambda s0: s0.gen.ancestors and s0.parent == s
                if isinstance(h, DeepHistoryState):
                    f = lambda s0: not s0.gen.descendants and s0 in s.gen.descendants
                self.history_values[h.gen.state_id] = list(filter(f, self.configuration))

        ctx = EvalContext(current_state=self, events=events, memory=self.rhs_memory)

        print_debug("fire " + str(t))
        for s in exit_set:
            print_debug(termcolor.colored('  EXIT %s' % s.gen.full_name, 'green'))
            self.eventless_states -= s.gen.has_eventless_transitions
            # execute exit action(s)
            self._perform_actions(ctx, s.exit)
            # self.rhs_memory.pop_local_scope(s.scope)
            self.configuration_bitmap &= ~s.gen.state_id_bitmap
                
        # execute transition action(s)
        self.rhs_memory.push_frame(t.scope) # make room for event parameters on stack
        self._copy_event_params_to_stack(self.rhs_memory, t, events)
        self._perform_actions(ctx, t.actions)
        self.rhs_memory.pop_frame()
            
        # enter states...
        targets = __getEffectiveTargetStates()
        enter_set = __enterSet(targets)
        for s in enter_set:
            print_debug(termcolor.colored('  ENTER %s' % s.gen.full_name, 'green'))
            self.eventless_states += s.gen.has_eventless_transitions
            self.configuration_bitmap |= s.gen.state_id_bitmap
            # execute enter action(s)
            self._perform_actions(ctx, s.enter)
            self._start_timers(s.gen.after_triggers)
        try:
            self.configuration = self.config_mem[self.configuration_bitmap]
        except KeyError:
            self.configuration = self.config_mem[self.configuration_bitmap] = [s for s in self.model.tree.state_list if self.configuration_bitmap & s.gen.state_id_bitmap]

        self.rhs_memory.flush_transition()

    @staticmethod
    def _copy_event_params_to_stack(memory, t, events):
        # Both 'events' and 't.trigger.enabling' are sorted by event ID...
        # This way we have to iterate over each of both lists at most once.
        if t.trigger and not isinstance(t.trigger, AfterTrigger):
            event_decls = iter(t.trigger.enabling)
            try:
                event_decl = next(event_decls)
                offset = 0
                for e in events:
                    if e.id < event_decl.id:
                        continue
                    else:
                        while e.id > event_decl.id:
                            event_decl = next(event_decls)
                        for p in e.params:
                            memory.store(offset, p)
                            offset += 1
            except StopIteration:
                pass

    def check_guard(self, t, events) -> bool:
        # Special case: after trigger
        if isinstance(t.trigger, AfterTrigger):
            e = [e for e in events if bit(e.id) & t.trigger.enabling_bitmap][0] # it's safe to assume the list will contain one element cause we only check a transition's guard after we know it may be enabled given the set of events
            if self.timer_ids[t.trigger.after_id] != e.params[0]:
                return False

        if t.guard is None:
            return True
        else:
            # print("evaluating guard for ", str(t))
            self.gc_memory.push_frame(t.scope)
            self._copy_event_params_to_stack(self.gc_memory, t, events)
            result = t.guard.eval(
                EvalContext(current_state=self, events=events, memory=self.gc_memory))
            self.gc_memory.pop_frame()
            self.gc_memory.flush_transition()
            # print("done with guard for ", str(t))
            return result

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
            self.gc_memory.flush_transition()
            timer_id = self._next_timer_id(after)
            self.output.append(OutputEvent(
                Event(id=after.id, name=after.name, params=[timer_id]),
                target=InstancesTarget([self.instance]),
                time_offset=delay))

    def _next_timer_id(self, trigger: AfterTrigger):
        self.timer_ids[trigger.after_id] += 1
        return self.timer_ids[trigger.after_id]

    # Return whether the current configuration includes ALL the states given.
    def in_state(self, state_strings: List[str]) -> bool:
        state_ids_bitmap = Bitmap.from_list((self.model.tree.state_dict[state_string].gen.state_id for state_string in state_strings))
        in_state = self.configuration_bitmap.has_all(state_ids_bitmap)
        # if in_state:
        #     print_debug("in state"+str(state_strings))
        # else:
        #     print_debug("not in state"+str(state_strings))
        return in_state

    def collect_output(self) -> Tuple[bool, List[OutputEvent]]:
        output = self.output
        self.output = []
        return (not self.eventless_states, output)
