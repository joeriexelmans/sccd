from typing import *
from dataclasses import *
from sccd.util.bitmap import *
from sccd.util.debug import *
from sccd.action_lang.static.scope import *
from sccd.action_lang.dynamic.exceptions import *
from sccd.action_lang.static.expression import *

@dataclass(frozen=True)
class StackFrame:
  __slots__ = ["storage", "parent", "context", "scope"]

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

class Memory(MemoryInterface):
  __slots__ = ["_current_frame"]

  def __init__(self):
    self._current_frame = None

  def current_frame(self) -> StackFrame:
    return self._current_frame

  # For function calls: context MAY differ from _current_frame if the function was
  # called from a different context from where it was created.
  # This enables function closures.
  def push_frame_w_context(self, scope: Scope, context: StackFrame):
    self._current_frame = StackFrame(
      storage=[None]*scope.size(),
      parent=self._current_frame,
      context=context,
      scope=scope)

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
