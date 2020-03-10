import termcolor
import functools
from typing import List, Tuple, Iterable
from sccd.runtime.event_queue import Timestamp
from sccd.runtime.statechart_syntax import *
from sccd.runtime.event import *
from sccd.runtime.semantic_options import *
from sccd.runtime.debug import print_debug
from sccd.runtime.bitmap import *
from sccd.runtime.model import *
from sccd.runtime.round import *

ELSE_GUARD = "ELSE_GUARD"

class StatechartInstance(Instance):
    def __init__(self, statechart: Statechart, object_manager):
        self.statechart = statechart
        self.object_manager = object_manager


        semantics = statechart.semantics

        if semantics.has_wildcard():
            raise Exception("Model semantics has unexpanded wildcard for some fields.")

        # generator = CandidatesGeneratorEventBased(self)
        generator = CandidatesGeneratorCurrentConfigBased(self)
        small_step = SmallStep(termcolor.colored("small", 'blue'), generator)

        # Always add a layer of 'fairness' above our small steps, so
        # orthogonal transitions take turns fairly.
        combo_one = SuperRound(termcolor.colored("combo_one", 'cyan'), small_step, take_one=True)

        if semantics.big_step_maximality == BigStepMaximality.TAKE_ONE:
            self._big_step = combo_step = combo_one # No combo steps

        elif semantics.big_step_maximality == BigStepMaximality.TAKE_MANY:

            if semantics.combo_step_maximality == ComboStepMaximality.COMBO_TAKE_ONE:
                # Fairness round becomes our combo step round
                combo_step = combo_one
            elif semantics.combo_step_maximality == ComboStepMaximality.COMBO_TAKE_MANY:
                # Add even more layers, basically an onion at this point.
                combo_step = SuperRound(termcolor.colored("combo_many", 'magenta'), combo_one, take_one=False)

            self._big_step = SuperRound(termcolor.colored("big_many", 'red'), combo_step, take_one=False)

        if semantics.input_event_lifeline == InputEventLifeline.WHOLE:
            self.input_event_round = self._big_step
        elif semantics.input_event_lifeline == InputEventLifeline.FIRST_COMBO_STEP:
            self.input_event_round = combo_step
        elif semantics.input_event_lifeline == InputEventLifeline.FIRST_SMALL_STEP:
            self.input_event_round = small_step

        if semantics.internal_event_lifeline == InternalEventLifeline.QUEUE:
            self.raise_internal = lambda e: self.output_events.append(OutputEvent(e, InstancesTarget([self])))
        elif semantics.internal_event_lifeline == InternalEventLifeline.NEXT_COMBO_STEP:
            self.raise_internal = combo_step.add_next_event
        elif semantics.internal_event_lifeline == InternalEventLifeline.NEXT_SMALL_STEP:
            self.raise_internal = small_step.add_next_event

        print_debug("Round hierarchy:")
        s = small_step
        i=0
        while s:
            print_debug(str(i)+': '+s.name)
            i += 1
            s = s.parent

        self.data_model = DataModel({
            "INSTATE": Variable(self.in_state),
        })

        # these 2 fields have the same information
        self.configuration = []
        self.configuration_bitmap = Bitmap()

        self.eventless_states = 0 # number of states in current configuration that have at least one eventless outgoing transition.

        # mapping from configuration_bitmap (=int) to configuration (=List[State])
        self.config_mem = {}
        # mapping from history state id to states to enter if history is target of transition
        self.history_values = {}

    # enter default states, generating a set of output events
    def initialize(self, now: Timestamp) -> Tuple[bool, List[OutputEvent]]:
        self.output_events = []

        states = self.statechart.tree.root.getEffectiveTargetStates(self)
        self.configuration.extend(states)
        self.configuration_bitmap = Bitmap.from_list(s.state_id for s in states)
        for state in states:
            print_debug(termcolor.colored('  ENTER %s'%state.name, 'green'))
            self.eventless_states += state.has_eventless_transitions
            self._perform_actions(state.enter)
            self._start_timers(state.after_triggers)
        stable = not self.eventless_states
        print_debug(termcolor.colored('completed initialization (time=%d)'%now+("(stable)" if stable else ""), 'red'))
        return (stable, self.output_events)

    # perform a big step. generating a set of output events
    def big_step(self, now: Timestamp, input_events: List[Event]) -> Tuple[bool, List[OutputEvent]]:

        # print_debug(termcolor.colored('attempting big step, input_events='+str(input_events), 'red'))

        self.output_events = []

        self.input_event_round.remainder_events = input_events
        arenas_changed = self._big_step.run()

        # can the next big step still contain transitions, even if there are no input events?
        stable = not self.eventless_states or (not input_events and not arenas_changed)

        # if arenas_changed:
        #     print_debug(termcolor.colored('completed big step (time=%d)'%now+(" (stable)" if stable else ""), 'red'))
        # else:
        #     print_debug(termcolor.colored("(stable)" if stable else "", 'red'))

        return (stable, self.output_events)

    def _check_guard(self, t, events) -> bool:
        if t.guard is None:
            return True
        else:
            return t.guard.eval(events, self.data_model)

    def _check_source(self, t) -> bool:
        return self.configuration_bitmap.has(t.source.state_id)

    # @profile
    def _fire_transition(self, t: Transition) -> Bitmap:

        def __exitSet():
            return [s for s in reversed(t.lca.descendants) if (s in self.configuration)]
        
        def __enterSet(targets):
            target = targets[0]
            for a in reversed(target.ancestors):
                if a in t.source.ancestors:
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
            for h in s.history:
                f = lambda s0: s0.ancestors and s0.parent == s
                if isinstance(h, DeepHistoryState):
                    f = lambda s0: not s0.descendants and s0 in s.descendants
                self.history_values[h.state_id] = list(filter(f, self.configuration))
        # print_debug('')
        print_debug(termcolor.colored('transition  %s 🡪 %s'%(t.source.name, t.targets[0].name), 'green'))
        for s in exit_set:
            print_debug(termcolor.colored('  EXIT %s' % s.name, 'green'))
            self.eventless_states -= s.has_eventless_transitions
            # execute exit action(s)
            self._perform_actions(s.exit)
            self.configuration_bitmap &= ~Bit(s.state_id)
                
        # execute transition action(s)
        self._perform_actions(t.actions)
            
        # enter states...
        targets = __getEffectiveTargetStates()
        enter_set = __enterSet(targets)
        for s in enter_set:
            print_debug(termcolor.colored('  ENTER %s' % s.name, 'green'))
            self.eventless_states += s.has_eventless_transitions
            self.configuration_bitmap |= Bit(s.state_id)
            # execute enter action(s)
            self._perform_actions(s.enter)
            self._start_timers(s.after_triggers)
        try:
            self.configuration = self.config_mem[self.configuration_bitmap]
        except:
            self.configuration = self.config_mem[self.configuration_bitmap] = [s for s in self.statechart.tree.state_list if self.configuration_bitmap.has(s.state_id)]

        return t.arena_bitmap
        
    def _perform_actions(self, actions: List[Action]):
        for a in actions:
            if isinstance(a, RaiseInternalEvent):
                self.raise_internal(Event(id=a.event_id, name=a.name, port="", parameters=[]))
            elif isinstance(a, RaiseOutputEvent):
                self.output_events.append(
                    OutputEvent(Event(id=0, name=a.name, port=a.outport, parameters=[]),
                    OutputPortTarget(a.outport),
                    a.time_offset))

    def _start_timers(self, triggers: List[AfterTrigger]):
        for after in triggers:
            self.output_events.append(OutputEvent(
                Event(id=after.id, name=after.name, parameters=[after.nextTimerId()]),
                target=InstancesTarget([self]),
                time_offset=after.delay))

    # Return whether the current configuration includes ALL the states given.
    def in_state(self, state_strings: List[str]) -> bool:
        state_ids_bitmap = Bitmap.from_list((self.statechart.tree.states[state_string].state_id for state_string in state_strings))
        in_state = self.configuration_bitmap.has_all(state_ids_bitmap)
        if in_state:
            print_debug("in state"+str(state_strings))
        else:
            print_debug("not in state"+str(state_strings))
        return in_state

