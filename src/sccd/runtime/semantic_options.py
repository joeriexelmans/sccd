from enum import Enum
from dataclasses import dataclass

class BigStepMaximality(Enum):
  TAKE_ONE = 0
  TAKE_MANY = 1

class ComboStepMaximality(Enum):
  COMBO_TAKE_ONE = 0
  COMBO_TAKE_MANY = 1


class InternalEventLifeline(Enum):
  QUEUE = 0
  NEXT_SMALL_STEP = 1
  NEXT_COMBO_STEP = 2

class InputEventLifeline(Enum):
  WHOLE = 0
  FIRST_SMALL_STEP = 1
  FIRST_COMBO_STEP = 2

class Priority(Enum):
  SOURCE_PARENT = 0
  SOURCE_CHILD = 1

class Concurrency(Enum):
  SINGLE = 0
  MANY = 1

@dataclass
class SemanticConfiguration:
  big_step_maximality: BigStepMaximality = BigStepMaximality.TAKE_MANY
  combo_step_maximality: ComboStepMaximality = ComboStepMaximality.COMBO_TAKE_ONE
  internal_event_lifeline: InternalEventLifeline = InternalEventLifeline.NEXT_COMBO_STEP
  input_event_lifeline: InputEventLifeline = InputEventLifeline.FIRST_COMBO_STEP
  priority: Priority = Priority.SOURCE_PARENT
  concurrency: Concurrency = Concurrency.SINGLE
