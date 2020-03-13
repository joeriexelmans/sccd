import termcolor
import functools
from typing import List, Tuple, Iterable
from sccd.execution.instance import *
from sccd.syntax.statechart import *
# from sccd.execution.event import *
# from sccd.runtime.semantic_options import *
from sccd.util.debug import print_debug
from sccd.util.bitmap import *
# from sccd.model.model import *
from sccd.execution.round import *
from sccd.execution.statechart_state import *

class StatechartInstance(Instance):
    def __init__(self, statechart: Statechart, object_manager):
        self.statechart = statechart
        self.object_manager = object_manager

        semantics = statechart.semantics

        if semantics.has_wildcard():
            raise Exception("Model semantics has unexpanded wildcard for some fields.")

        reverse = semantics.priority == Priority.SOURCE_CHILD

        generator = CandidatesGeneratorCurrentConfigBased(reverse)
        # generator = CandidatesGeneratorEventBased(reverse)

        small_step = SmallStep(termcolor.colored("small", 'blue'), None, generator)

        # Always add a layer of 'fairness' above our small steps, so
        # orthogonal transitions take turns fairly.
        combo_one = SuperRound(termcolor.colored("combo_one", 'magenta'), small_step, take_one=True)

        if semantics.big_step_maximality == BigStepMaximality.TAKE_ONE:
            self._big_step = combo_step = combo_one # No combo steps

        elif semantics.big_step_maximality == BigStepMaximality.TAKE_MANY:

            if semantics.combo_step_maximality == ComboStepMaximality.COMBO_TAKE_ONE:
                # Fairness round becomes our combo step round
                combo_step = combo_one
            elif semantics.combo_step_maximality == ComboStepMaximality.COMBO_TAKE_MANY:
                # Add even more layers, basically an onion at this point.
                combo_step = SuperRound(termcolor.colored("combo_many", 'cyan'), combo_one, take_one=False)

            self._big_step = SuperRound(termcolor.colored("big_many", 'red'), combo_step, take_one=False)

        def whole(input):
            self._big_step.remainder_events = input

        def first_combo(input):
            combo_step.remainder_events = input

        def first_small(input):
            small_step.remainder_events = input

        self.set_input = {
            InputEventLifeline.WHOLE: whole,
            InputEventLifeline.FIRST_COMBO_STEP: first_combo,
            InputEventLifeline.FIRST_SMALL_STEP: first_small
        }[semantics.input_event_lifeline]

        raise_internal = {
            InternalEventLifeline.QUEUE: lambda e: self.state.output.append(OutputEvent(e, InstancesTarget([self]))),
            InternalEventLifeline.NEXT_COMBO_STEP: combo_step.add_next_event,
            InternalEventLifeline.NEXT_SMALL_STEP: small_step.add_next_event
        }[semantics.internal_event_lifeline]

        print_debug("\nRound hierarchy: " + str(self._big_step) + '\n')

        self.state = StatechartState(statechart, self, raise_internal)

        small_step.state = self.state


    # enter default states, generating a set of output events
    def initialize(self, now: Timestamp) -> Tuple[bool, List[OutputEvent]]:
        self.state.initialize()
        stable, output = self.state.collect_output()

        print_debug('completed initialization (time=%d)'%now+("(stable)" if stable else ""))

        return (stable, output)

    # perform a big step. generating a set of output events
    def big_step(self, now: Timestamp, input_events: List[Event]) -> Tuple[bool, List[OutputEvent]]:

        # print_debug(termcolor.colored('attempting big step, input_events='+str(input_events), 'red'))

        self.set_input(input_events)

        arenas_changed = self._big_step.run()

        stable, output = self.state.collect_output()

        # can the next big step still contain transitions, even if there are no input events?
        stable |= not input_events and not arenas_changed

        # if arenas_changed:
        #     print_debug(termcolor.colored('completed big step (time=%d)'%now+(" (stable)" if stable else ""), 'red'))
        # else:
        #     print_debug(termcolor.colored("(stable)" if stable else "", 'red'))

        return (stable, output)
