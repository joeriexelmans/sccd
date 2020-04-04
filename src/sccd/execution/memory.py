from typing import *
from dataclasses import *
from sccd.util.bitmap import *
from sccd.util.debug import *
from sccd.syntax.scope import *

@dataclass(frozen=True)
class StackFrame:
  # Values of variables in the frame.
  storage: List[Any]

  # The previous stack frame, forming a linked list of stack frames representing the "call stack".
  # The parent frame will become the "current frame" when this stack frame is popped.
  parent: Optional['StackFrame']

  # The sequence of 'context' values forms another linked list, often but not always identical to the linked list of 'parent's, for accessing nonlocal variables.
  # The 'context' is the stack frame in which the frame of the currently called function was declared.
  # This could be a stack frame that no longer exists on "the stack", like with a function closure, or some ancestor, for a recursive function.
  # If the current scope is not a function, this value is equal to the 'parent' field.
  context: Optional['StackFrame']

  # We need this to know where the offsets of this scope start relative to the offsets of the parent scope, and to print variable names in error messages.
  scope: Scope

  def __str__(self):
    def short_descr(frame):
      return "StackFrame(%s, len=%d, ...)" % (frame.scope.name, len(frame.storage)) if frame else "None"

    return "StackFrame(%s, len=%d, parent=%s, context=%s)" % (self.scope.name, len(self.storage), short_descr(self.parent), "parent" if self.context is self.parent else short_descr(self.context))


class MemoryInterface(ABC):

  @abstractmethod
  def current_frame(self) -> StackFrame:
    pass

  @abstractmethod
  def push_frame(self, scope: Scope):
    pass

  @abstractmethod
  def push_frame_w_context(self, scope: Scope, context: StackFrame):
    pass

  @abstractmethod
  def pop_frame(self):
    pass

  @abstractmethod
  def load(self, offset: int) -> Any:
    pass

  @abstractmethod
  def store(self, offset: int, value: Any):
    pass


class Memory(MemoryInterface):

  def __init__(self):
    self._current_frame = None

  def current_frame(self) -> StackFrame:
    return self._current_frame

  def push_frame_w_context(self, scope: Scope, context: StackFrame):

    self._current_frame = StackFrame(
      storage=[None]*scope.size(),
      parent=self._current_frame,
      context=context,
      scope=scope)

  # For function calls: context MAY differ from _current_frame if the function was
  # called from a different context from where it was created.
  # This enables function closures.
  def push_frame(self, scope: Scope):
    self.push_frame_w_context(scope, self._current_frame)

  def pop_frame(self):
    self._current_frame = self._current_frame.parent

  def _get_frame(self, offset: int) -> Tuple[StackFrame, int]:
    frame = self._current_frame
    while offset < 0:
      offset += frame.scope.parent_offset
      frame = frame.context

    return (frame, offset)

  def load(self, offset: int) -> Any:
    frame, offset = self._get_frame(offset)
    return frame.storage[offset]

  def store(self, offset: int, value: Any):
    frame, offset = self._get_frame(offset)
    frame.storage[offset] = value


class MemoryPartialSnapshot(MemoryInterface):

  def __init__(self, memory: Memory):
    self.memory = memory
    self.frame = memory.current_frame()

    self.actual: List[Any] = self.frame.storage
    self.snapshot: List[Any] = list(self.actual)

    # Positions in stack frame written to by current transition.
    self.trans_dirty = Bitmap()

    # Positions in stack frame written to during current big, combo or small step (depending on semantic option chosen)
    self.round_dirty = Bitmap()

  def current_frame(self) -> StackFrame:
    return self.memory.current_frame()

  def push_frame(self, scope: Scope):
    return self.memory.push_frame(scope)

  def push_frame_w_context(self, scope: Scope, context: StackFrame):
    return self.memory.push_frame_w_context(scope, context)

  def pop_frame(self):
    # The frame we are snapshotting should never be popped.
    assert self.memory.current_frame() is not self.frame

    return self.memory.pop_frame()

  def load(self, offset: int) -> Any:
    frame, offset = self.memory._get_frame(offset)
    # Sometimes read from snapshot
    if frame is self.frame:
      # "our" frame! :)
      if self.trans_dirty.has(offset):
        return self.actual[offset]
      else:
        return self.snapshot[offset]
    else:
      return frame.storage[offset]

  def store(self, offset: int, value: Any):
    frame, offset = self.memory._get_frame(offset)
    # Always write to 'actual' storage
    frame.storage[offset] = value

    if frame is self.frame:
      # "our" frame! :)
      # Remember that we wrote, such that next read during same transition will be the value we wrote.
      self.trans_dirty |= bit(offset)

  def flush_transition(self):  
    race_conditions = self.trans_dirty & self.round_dirty
    if race_conditions:
      variables = self.frame.scope.variables
      # some variable written to twice before refresh
      raise Exception("Race condition for variables %s" %
          ", ".join(variables[offset].name for offset in race_conditions.items()))

    self.round_dirty |= self.trans_dirty
    self.trans_dirty = Bitmap() # reset

  def flush_round(self):
    assert not self.trans_dirty # only allowed to be called right after flush_temp

    # Probably quickest to just copy the entire list in Python
    self.snapshot = list(self.actual) # refresh
    self.round_dirty = Bitmap() # reset
