from sccd.action_lang.dynamic.memory import *
from sccd.util import timer

# Non-snapshotting memory. Basically delegates all operations.
class StatechartMemory(MemoryInterface):
  __slots__ = ["delegate"]

  def __init__(self, delegate: MemoryInterface):
    self.delegate = delegate

  def current_frame(self) -> StackFrame:
    return self.delegate.current_frame()

  def push_frame(self, scope: Scope):
    return self.delegate.push_frame(scope)

  def push_frame_w_context(self, scope: Scope, context: StackFrame):
    return self.delegate.push_frame_w_context(scope, context)

  def pop_frame(self):
    return self.delegate.pop_frame()

  def load(self, offset: int) -> Any:
    return self.delegate.load(offset)

  def store(self, offset: int, value: Any):
    self.delegate.store(offset, value)

  def _get_frame(self, offset):
    return self.delegate._get_frame(offset)

  def flush_transition(self):
    pass

  def flush_round(self):
    pass

# Snapshotting memory. Takes snapshots of a single frame in memory.
class SnapshottingStatechartMemory(StatechartMemory):
  __slots__ = ["frame", "actual", "snapshot", "trans_dirty", "round_dirty"]

  def __init__(self, delegate: MemoryInterface, frame: StackFrame):
    super().__init__(delegate)

    self.frame = frame # frame to be snapshotted

    self.actual: List[Any] = self.frame.storage
    self.snapshot: List[Any] = list(self.actual)

    # Positions in stack frame written to by current transition.
    self.trans_dirty = Bitmap()

    # Positions in stack frame written to during current big, combo or small step (depending on semantic option chosen)
    self.round_dirty = Bitmap()

  # override
  def load(self, offset: int) -> Any:
    frame, offset = self.delegate._get_frame(offset)
    # Sometimes read from snapshot
    if frame is self.frame:
      # "our" frame! :)
      if bm_has(self.trans_dirty, offset):
        return self.actual[offset]
      else:
        return self.snapshot[offset]
    else:
      return frame.storage[offset]

  # override
  def store(self, offset: int, value: Any):
    frame, offset = self.delegate._get_frame(offset)
    if frame is self.frame:
      # Remember that we wrote, such that next read during same transition will be the value we wrote.
      self.trans_dirty |= bit(offset)

    # Always write to 'actual' storage
    frame.storage[offset] = value

  # override
  def flush_transition(self):
    race_conditions = self.trans_dirty & self.round_dirty
    if race_conditions:
      variables = self.frame.scope.variables
      # some variable written to twice before refresh
      raise SCCDRuntimeException("Race condition: More than one transition assigned a new value to variables: %s" % (", ".join(variables[offset].name for offset in bm_items(race_conditions))))

    self.round_dirty |= self.trans_dirty
    self.trans_dirty = Bitmap() # reset

  # override
  def flush_round(self):
    assert not self.trans_dirty # only allowed to be called right after flush_temp

    # Probably quickest to just copy the entire list in Python
    self.snapshot = list(self.actual) # refresh
    self.round_dirty = Bitmap() # reset

# Treats a single frame in memory as read-only.
class ReadOnlyStatechartMemory(StatechartMemory):
  __slots__ = ["frame"]

  def __init__(self, delegate: StatechartMemory, frame: StackFrame):
    super().__init__(delegate)
    self.frame = frame

  # override
  def store(self, offset: int, value: Any):
    frame, offset = self.delegate._get_frame(offset)
    if frame is self.frame:
      raise SCCDRuntimeException("Attempt to write to read-only memory.")

    self.delegate.store(offset, value)

  # override
  def flush_transition(self):
    self.delegate.flush_transition()

  # override
  def flush_round(self):
    self.delegate.flush_round()
