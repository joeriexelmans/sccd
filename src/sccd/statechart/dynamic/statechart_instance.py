import termcolor
import functools
from typing import List, Tuple, Iterable
from sccd.util.debug import print_debug
from sccd.util.bitmap import *
from sccd.statechart.static.statechart import *
from sccd.statechart.dynamic.builtin_scope import *
from sccd.statechart.dynamic.round import *
from sccd.statechart.dynamic.statechart_execution import *
from sccd.statechart.dynamic.memory_snapshot import *

# Interface for all instances and also the Object Manager
class Instance(ABC):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def big_step(self, input_events: List[InternalEvent]):
        pass

# Hardcoded limit on number of sub-rounds of combo and big step to detect never-ending superrounds.
# TODO: make this configurable
LIMIT = 100

class StatechartInstance(Instance):
    def __init__(self, statechart: Statechart, object_manager, output_callback, schedule_callback, cancel_callback):
        # self.object_manager = object_manager
        self.output_callback = output_callback

        self.execution = StatechartExecution(self, statechart)

        semantics = statechart.semantics

        if semantics.has_multiple_variants():
            raise Exception("Cannot execute model with multiple semantics.")

        reverse = semantics.priority == Priority.SOURCE_CHILD

        # 2 transition candidate generation algorithms to choose from!
        # generator = CandidatesGeneratorCurrentConfigBased(statechart, reverse)
        generator = CandidatesGeneratorEventBased(statechart, reverse)

        # Big step + combo step maximality semantics

        small_step = SmallStep(termcolor.colored("small", 'blue'), self.execution, generator,
            concurrency=semantics.concurrency==Concurrency.MANY)


        if semantics.big_step_maximality == BigStepMaximality.TAKE_ONE:
            self._big_step = combo_step = SuperRound(termcolor.colored("big_one", 'red'), small_step, maximality=TakeOne()) # No combo steps

        elif semantics.big_step_maximality == BigStepMaximality.TAKE_MANY or semantics.big_step_maximality == BigStepMaximality.SYNTACTIC:
            # Always add a layer of 'fairness' above our small steps, so
            # orthogonal transitions take turns fairly.
            combo_one = SuperRound(termcolor.colored("combo_one", 'magenta'), small_step, maximality=TakeOne())

            if semantics.combo_step_maximality == ComboStepMaximality.COMBO_TAKE_ONE:
                # Fairness round becomes our combo step round
                combo_step = combo_one

            elif semantics.combo_step_maximality == ComboStepMaximality.COMBO_TAKE_MANY:
                # Add even more layers, basically an onion at this point.
                combo_step = SuperRoundWithLimit(termcolor.colored("combo_many", 'cyan'), combo_one, maximality=TakeMany(), limit=LIMIT)

            else:
                raise Exception("Unsupported option: %s" % semantics.combo_step_maximality)

            if semantics.big_step_maximality == BigStepMaximality.TAKE_MANY:
                self._big_step = SuperRoundWithLimit(termcolor.colored("big_many", 'red'), combo_step, maximality=TakeMany(), limit=LIMIT)
            else:
                self._big_step = SuperRoundWithLimit(termcolor.colored("big_syntactic", 'red'), combo_step, maximality=Syntactic(), limit=LIMIT)

        else:
            raise Exception("Unsupported option: %s" % semantics.big_step_maximality)

        # Event lifeline semantics

        def whole(input):
            self._big_step.remainder_events.extend(input)

        def first_combo(input):
            combo_step.remainder_events.extend(input)

        def first_small(input):
            small_step.remainder_events.extend(input)

        self.set_input = {
            InputEventLifeline.WHOLE: whole,
            InputEventLifeline.FIRST_COMBO_STEP: first_combo,
            InputEventLifeline.FIRST_SMALL_STEP: first_small
        }[semantics.input_event_lifeline]


        self.self_list = [self]
        
        raise_internal = {
            InternalEventLifeline.QUEUE: lambda e: schedule_callback(0, e, self.self_list),
            InternalEventLifeline.NEXT_COMBO_STEP: combo_step.add_next_event,
            InternalEventLifeline.NEXT_SMALL_STEP: small_step.add_next_event,
            InternalEventLifeline.REMAINDER: self._big_step.add_remainder_event,
            InternalEventLifeline.SAME: small_step.add_remainder_event,
        }[semantics.internal_event_lifeline]

        # Memory protocol semantics

        memory = Memory()
        load_builtins(memory, self.execution)
        memory.push_frame(statechart.scope)

        rhs_memory = MemoryPartialSnapshot("RHS", memory)

        if semantics.assignment_memory_protocol == MemoryProtocol.BIG_STEP:
            self._big_step.when_done(rhs_memory.flush_round)
        elif semantics.enabledness_memory_protocol == MemoryProtocol.COMBO_STEP:
            combo_step.when_done(rhs_memory.flush_round)
        elif semantics.enabledness_memory_protocol == MemoryProtocol.SMALL_STEP:
            small_step.when_done(rhs_memory.flush_round)

        gc_memory = MemoryPartialSnapshot("GC", memory, read_only=True)

        if semantics.assignment_memory_protocol == MemoryProtocol.BIG_STEP:
            self._big_step.when_done(gc_memory.flush_round)
        elif semantics.assignment_memory_protocol == MemoryProtocol.COMBO_STEP:
            combo_step.when_done(gc_memory.flush_round)
        elif semantics.assignment_memory_protocol == MemoryProtocol.SMALL_STEP:
            small_step.when_done(gc_memory.flush_round)

        print_debug("\nRound hierarchy: " + str(self._big_step) + '\n')

        self.execution.gc_memory = gc_memory
        self.execution.rhs_memory = rhs_memory
        self.execution.raise_internal = raise_internal
        self.execution.schedule_callback = schedule_callback
        self.execution.cancel_callback = cancel_callback
        self.execution.raise_output = output_callback


    # enter default states, generating a set of output events
    def initialize(self):
        self.execution.initialize()
        self.output_callback(OutputEvent(port="trace", name="big_step_completed", params=self.self_list))

    # perform a big step. generating a set of output events
    def big_step(self, input_events: List[InternalEvent]):
        # print_debug('attempting big step, input_events='+str(input_events))
        self.set_input(input_events)
        self._big_step.run_and_cycle_events()

        self.output_callback(OutputEvent(port="trace", name="big_step_completed", params=self.self_list))
