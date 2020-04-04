from enum import *
from dataclasses import *
from typing import *
import itertools
from sccd.syntax.tree import *
from sccd.syntax.scope import *

class SemanticAspect:
  def __str__(self):
    # Override default: only print field, not the type (e.g. "TAKE_ONE" instead of "BigStepMaximality.TAKE_ONE")
    return self.name

class BigStepMaximality(SemanticAspect, Enum):
  TAKE_ONE = auto()
  TAKE_MANY = auto()
  SYNTACTIC = auto()

class ComboStepMaximality(SemanticAspect, Enum):
  COMBO_TAKE_ONE = auto()
  COMBO_TAKE_MANY = auto()

class InternalEventLifeline(SemanticAspect, Enum):
  QUEUE = auto()
  NEXT_COMBO_STEP = auto()
  NEXT_SMALL_STEP = auto()

  REMAINDER = auto()
  SAME = auto()

class InputEventLifeline(SemanticAspect, Enum):
  WHOLE = auto()
  FIRST_COMBO_STEP = auto()
  FIRST_SMALL_STEP = auto()

class MemoryProtocol(SemanticAspect, Enum):
  BIG_STEP = auto()
  COMBO_STEP = auto()
  SMALL_STEP = auto()
  # NONE = auto()

class Priority(SemanticAspect, Enum):
  SOURCE_PARENT = auto()
  SOURCE_CHILD = auto()

class Concurrency(SemanticAspect, Enum):
  SINGLE = auto()
  MANY = auto()

_T = TypeVar('T', bound=SemanticAspect)
SemanticChoice = Union[_T, List[_T]]

@dataclass
class SemanticConfiguration:
  # All semantic aspects and their default values.
  # Every field can be set to a list of multiple options, or just a value.
  big_step_maximality: SemanticChoice[BigStepMaximality] = BigStepMaximality.TAKE_MANY
  combo_step_maximality: SemanticChoice[ComboStepMaximality] = ComboStepMaximality.COMBO_TAKE_ONE
  internal_event_lifeline: SemanticChoice[InternalEventLifeline] = InternalEventLifeline.NEXT_COMBO_STEP
  input_event_lifeline: SemanticChoice[InputEventLifeline] = InputEventLifeline.FIRST_COMBO_STEP
  enabledness_memory_protocol: SemanticChoice[MemoryProtocol] = MemoryProtocol.COMBO_STEP
  assignment_memory_protocol: SemanticChoice[MemoryProtocol] = MemoryProtocol.COMBO_STEP
  priority: SemanticChoice[Priority] = Priority.SOURCE_PARENT
  concurrency: SemanticChoice[Concurrency] = Concurrency.SINGLE

  @classmethod
  def get_fields(cls) -> Iterator[Tuple[str, SemanticAspect]]:
    return ((f.name, type(f.default)) for  f in fields(cls))

  # Whether multiple options are set for any aspect.
  def has_multiple_variants(self) -> bool:
    for f in fields(self):
      if isinstance(getattr(self, f.name), list):
        return True
    return False

  # Get all possible combinations for aspects with multiple options (as a list) set.
  # Calling has_multiple_variants on resulting objects will return False.
  def generate_variants(self) -> List['SemanticConfiguration']:
    my_fields = fields(self)
    chosen_options = ([item] if not isinstance(item,list) else item for item in (getattr(self, f.name) for f in my_fields))
    variants = itertools.product(*chosen_options)

    return [SemanticConfiguration(**{f.name: o for f,o in zip(my_fields, variant)}) for variant in variants]

@dataclass
class Statechart:
  semantics: SemanticConfiguration

  scope: Scope
  datamodel: Optional[Block] # block of statements setting up the datamodel (variables in instance scope)

  inport_events: Dict[str, Set[int]] # mapping from inport to set of event IDs
  event_outport: Dict[str, str] # mapping from event name to outport

  tree: StateTree
