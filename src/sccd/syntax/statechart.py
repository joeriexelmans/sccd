from enum import *
from dataclasses import *
from typing import *
import itertools
from sccd.syntax.tree import *
from sccd.syntax.scope import *

class SemanticOption:

  def __str__(self):
    return self.name

class BigStepMaximality(SemanticOption, Enum):
  TAKE_ONE = 0
  TAKE_MANY = 1
  SYNTACTIC = 2

class ComboStepMaximality(SemanticOption, Enum):
  COMBO_TAKE_ONE = 0
  COMBO_TAKE_MANY = 1

class InternalEventLifeline(SemanticOption, Enum):
  QUEUE = 0
  NEXT_COMBO_STEP = 1
  NEXT_SMALL_STEP = 2

  REMAINDER = 3
  SAME = 5

class InputEventLifeline(SemanticOption, Enum):
  WHOLE = 0
  FIRST_COMBO_STEP = 1
  FIRST_SMALL_STEP = 2

class MemoryProtocol(SemanticOption, Enum):
  BIG_STEP = 0
  COMBO_STEP = 1
  SMALL_STEP = 2

class Priority(SemanticOption, Enum):
  SOURCE_PARENT = 0
  SOURCE_CHILD = 1

class Concurrency(SemanticOption, Enum):
  SINGLE = 0
  MANY = 1

@dataclass
class Semantics:
  big_step_maximality: BigStepMaximality = BigStepMaximality.TAKE_MANY
  combo_step_maximality: ComboStepMaximality = ComboStepMaximality.COMBO_TAKE_ONE
  internal_event_lifeline: InternalEventLifeline = InternalEventLifeline.NEXT_COMBO_STEP
  input_event_lifeline: InputEventLifeline = InputEventLifeline.FIRST_COMBO_STEP
  enabledness_memory_protocol: MemoryProtocol = MemoryProtocol.COMBO_STEP
  assignment_memory_protocol: MemoryProtocol = MemoryProtocol.COMBO_STEP
  priority: Priority = Priority.SOURCE_PARENT
  concurrency: Concurrency = Concurrency.SINGLE

# Semantics with multiple options per field
@dataclass
class VariableSemantics:
  big_step_maximality: List[BigStepMaximality] = field(default_factory=lambda:[BigStepMaximality.TAKE_MANY])
  combo_step_maximality: List[ComboStepMaximality] = field(default_factory=lambda:[ComboStepMaximality.COMBO_TAKE_ONE])
  internal_event_lifeline: List[InternalEventLifeline] = field(default_factory=lambda:[InternalEventLifeline.NEXT_COMBO_STEP])
  input_event_lifeline: List[InputEventLifeline] = field(default_factory=lambda:[InputEventLifeline.FIRST_COMBO_STEP])
  enabledness_memory_protocol: List[MemoryProtocol] = field(default_factory=lambda:[MemoryProtocol.COMBO_STEP])
  assignment_memory_protocol: List[MemoryProtocol] = field(default_factory=lambda:[MemoryProtocol.COMBO_STEP])
  priority: List[Priority] = field(default_factory=lambda:[Priority.SOURCE_PARENT])
  concurrency: List[Concurrency] = field(default_factory=lambda:[Concurrency.SINGLE])

  # Get all possible combinations
  def generate_variants(self) -> List[Semantics]:
    my_fields = fields(self)
    chosen_options = (getattr(self, f.name) for f in my_fields)
    variants = itertools.product(*chosen_options)

    return [Semantics(**{f.name: o for f,o in zip(my_fields, variant)}) for variant in variants]


@dataclass
class Statechart:
  inport_events: Dict[str, Set[int]] # mapping from inport to set of event IDs
  event_outport: Dict[str, str] # mapping from event name to outport

  semantics: Union[VariableSemantics, Semantics]
  tree: StateTree
  scope: Scope
