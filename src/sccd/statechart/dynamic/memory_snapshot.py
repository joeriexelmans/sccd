from sccd.action_lang.dynamic.memory import *
from sccd.util import timer

class MemoryPartialSnapshot(MemoryInterface):

  def __init__(self, description: str, memory: Memory, read_only: bool = False):
    self.description = description
    self.memory = memory
    self.read_only = read_only

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
      if bm_has(self.trans_dirty, offset):
        return self.actual[offset]
      else:
        return self.snapshot[offset]
    else:
      return frame.storage[offset]

  def store(self, offset: int, value: Any):
    frame, offset = self.memory._get_frame(offset)
    if frame is self.frame:
      if self.read_only:
        raise SCCDRuntimeException("Attempt to write to read-only %s memory." % self.description)
      # "our" frame! :)
      # Remember that we wrote, such that next read during same transition will be the value we wrote.
      self.trans_dirty |= bit(offset)

    # Always write to 'actual' storage
    frame.storage[offset] = value


  def flush_transition(self, read_only: bool = False):
    race_conditions = self.trans_dirty & self.round_dirty
    if race_conditions:
      variables = self.frame.scope.variables
      # some variable written to twice before refresh
      raise SCCDRuntimeException("Race condition in %s memory: More than one transition assigned a new value to variables: %s" %
          (self.description, ", ".join(variables[offset].name for offset in race_conditions.items())))

    self.round_dirty |= self.trans_dirty
    self.trans_dirty = Bitmap() # reset

  def flush_round(self):
    assert not self.trans_dirty # only allowed to be called right after flush_temp

    # Probably quickest to just copy the entire list in Python
    self.snapshot = list(self.actual) # refresh
    self.round_dirty = Bitmap() # reset
