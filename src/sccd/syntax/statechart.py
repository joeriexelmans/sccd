from enum import *
from dataclasses import *
from typing import *
import itertools
from sccd.syntax.tree import *

class BigStepMaximality(Enum):
  TAKE_ONE = 0
  TAKE_MANY = 1

class ComboStepMaximality(Enum):
  COMBO_TAKE_ONE = 0
  COMBO_TAKE_MANY = 1

class InternalEventLifeline(Enum):
  QUEUE = 0
  NEXT_COMBO_STEP = 1
  NEXT_SMALL_STEP = 2

class InputEventLifeline(Enum):
  WHOLE = 0
  FIRST_COMBO_STEP = 1
  FIRST_SMALL_STEP = 2

class Priority(Enum):
  SOURCE_PARENT = 0
  SOURCE_CHILD = 1

class Concurrency(Enum):
  SINGLE = 0
  MANY = 1

@dataclass
class Semantics:
  big_step_maximality: BigStepMaximality = BigStepMaximality.TAKE_MANY
  combo_step_maximality: ComboStepMaximality = ComboStepMaximality.COMBO_TAKE_ONE
  internal_event_lifeline: InternalEventLifeline = InternalEventLifeline.NEXT_COMBO_STEP
  input_event_lifeline: InputEventLifeline = InputEventLifeline.FIRST_COMBO_STEP
  priority: Priority = Priority.SOURCE_PARENT
  concurrency: Concurrency = Concurrency.SINGLE

  # Check if any field has been set to None.
  def has_wildcard(self):
    for field in fields(self):
      if getattr(self, field.name) is None:
        return True
    return False

  # List of mappings from field name to value for that field.
  # Each mapping in the list can be used as parameter to the dataclasses.replace function
  # to create a new semantic configuration with the changes applied.
  def wildcard_cart_product(self) -> Iterable[Mapping[str, Any]]:
    wildcard_fields = []
    for field in fields(self):
      if getattr(self, field.name) is None:
        wildcard_fields.append(field)
    types = (field.type for field in wildcard_fields)
    return ({wildcard_fields[i].name: option for i,option in enumerate(configuration)} for configuration in itertools.product(*types))

@dataclass
class Statechart:
  tree: StateTree
  semantics: Semantics
  datamodel: DataModel
