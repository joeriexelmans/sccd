from enum import *
from dataclasses import *
from typing import *
import itertools
from sccd.statechart.static.tree import *
from sccd.action_lang.static.scope import *

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

  ARENA_PARENT = auto()
  ARENA_CHILD = auto()

class Concurrency(SemanticAspect, Enum):
  SINGLE = auto()
  MANY = auto()

_T = TypeVar('_T', bound=SemanticAspect)
SemanticChoice = Union[_T, List[_T]]

@dataclass
class SemanticConfiguration:
  # All semantic aspects and their default values.
  # Every field can be set to a list of multiple options, or just a value.

  # The following is the default configuration:
  big_step_maximality: SemanticChoice[BigStepMaximality] = BigStepMaximality.TAKE_MANY
  combo_step_maximality: SemanticChoice[ComboStepMaximality] = ComboStepMaximality.COMBO_TAKE_ONE
  internal_event_lifeline: SemanticChoice[InternalEventLifeline] = InternalEventLifeline.NEXT_COMBO_STEP
  input_event_lifeline: SemanticChoice[InputEventLifeline] = InputEventLifeline.FIRST_COMBO_STEP
  enabledness_memory_protocol: SemanticChoice[MemoryProtocol] = MemoryProtocol.COMBO_STEP
  assignment_memory_protocol: SemanticChoice[MemoryProtocol] = MemoryProtocol.COMBO_STEP
  priority: SemanticChoice[Priority] = Priority.SOURCE_PARENT
  concurrency: SemanticChoice[Concurrency] = Concurrency.SINGLE

  def __str__(self):
    s = ""
    for f in fields(self):
      s += "\n  %s: %s" % (f.name, getattr(self, f.name))
    return s


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
class Statechart(Freezable):
  __slots__ = ["semantics", "scope", "datamodel", "internal_events", "internally_raised_events", "inport_events", "event_outport", "tree"]

  def __init__(self, semantics: SemanticConfiguration, scope: Scope, datamodel: Optional[Block], internal_events: Bitmap, internally_raised_events: Bitmap, inport_events: Dict[str, Set[int]], event_outport: Dict[str, str], tree: StateTree):
    
    super().__init__()
  
    # Semantic configuration for statechart execution
    self.semantics: SemanticConfiguration = semantics

    # Instance scope, the set of variable names (and their types and offsets in memory) that belong to the statechart
    self.scope: Scope = scope

    # Block of statements setting up the datamodel (variables in instance scope)
    self.datamodel: Optional[Block] = datamodel

    # Union of internally raised and input events. Basically all the events that a transition could be triggered by.
    self.internal_events: Bitmap = internal_events
    # All internally raised events in the statechart, may overlap with input events, as an event can be both an input event and internally raised.
    self.internally_raised_events: Bitmap = internally_raised_events

    # Mapping from inport to set of event IDs - currently unused
    self.inport_events: Dict[str, Bitmap] = inport_events
    # Mapping from event name to outport
    self.event_outport: Dict[str, str] = event_outport

    self.tree: StateTree = tree
