from enum import *
from dataclasses import *
from typing import *
import itertools

class SemanticAspect:
  def __str__(self):
    # Override default: only print field, not the type (e.g. "TAKE_ONE" instead of "BigStepMaximality.TAKE_ONE")
    return self.name

  __repr__ = __str__

class Maximality(SemanticAspect, Enum):
  TAKE_ONE = auto()
  SYNTACTIC = auto()
  TAKE_MANY = auto()

  # We define an ordering TAKE_ONE < SYNTACTIC < TAKE_MANY

  def __lt__(self, other):
    if self == other:
      return False
    if other == Maximality.TAKE_MANY:
      return True
    if other == Maximality.SYNTACTIC:
      return self == Maximality.TAKE_ONE
    return False

  def __le__(self, other):
    return self == other or self < other

  def __gt__(self, other):
    return not (self <= other)

  def __ge__(self, other):
    return not (self < other)

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

class HierarchicalPriority(SemanticAspect, Enum):
  NONE = auto()
  
  SOURCE_PARENT = auto()
  SOURCE_CHILD = auto()

  ARENA_PARENT = auto()
  ARENA_CHILD = auto()

class OrthogonalPriority(SemanticAspect, Enum):
  NONE = auto()
  EXPLICIT = auto()

class SameSourcePriority(SemanticAspect, Enum):
  NONE = auto()
  EXPLICIT = auto()

class Concurrency(SemanticAspect, Enum):
  SINGLE = auto()
  MANY = auto()

_T = TypeVar('_T', bound=SemanticAspect)
SemanticChoice = Union[_T, List[_T]]

@dataclass
class SemanticConfiguration:
  # All semantic aspects and their default values.
  # Every field can be set to a list of multiple options, or just a value.

  # The names of the fields of this class are used when parsing semantic options in the XML input format.

  # The following is the default configuration. Changing these values changes SCCD's default semantics:
  big_step_maximality: SemanticChoice[Maximality] = Maximality.TAKE_MANY
  combo_step_maximality: SemanticChoice[Maximality] = Maximality.TAKE_ONE
  internal_event_lifeline: SemanticChoice[InternalEventLifeline] = InternalEventLifeline.NEXT_COMBO_STEP
  input_event_lifeline: SemanticChoice[InputEventLifeline] = InputEventLifeline.FIRST_COMBO_STEP
  enabledness_memory_protocol: SemanticChoice[MemoryProtocol] = MemoryProtocol.SMALL_STEP
  assignment_memory_protocol: SemanticChoice[MemoryProtocol] = MemoryProtocol.SMALL_STEP

  hierarchical_priority: SemanticChoice[HierarchicalPriority] = HierarchicalPriority.SOURCE_PARENT
  orthogonal_priority: SemanticChoice[OrthogonalPriority] = OrthogonalPriority.EXPLICIT
  same_source_priority: SemanticChoice[SameSourcePriority] = SameSourcePriority.EXPLICIT
  
  concurrency: SemanticChoice[Concurrency] = Concurrency.SINGLE

  def __str__(self):
    s = ""
    for f in fields(self):
      s += "\n  %s: %s" % (f.name, getattr(self, f.name))
    return s


  @classmethod
  # def get_fields(cls) -> Iterator[Tuple[str, SemanticAspect]]:
  def get_fields(cls) -> Dict[str, SemanticAspect]:
    return {f.name: type(f.default) for  f in fields(cls)}

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
