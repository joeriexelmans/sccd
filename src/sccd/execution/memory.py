from typing import *
from sccd.util.bitmap import *
from sccd.util.debug import *

class Memory:
  def __init__(self, scope):
    self.scope = scope
    self.memory = [None] * scope.size()

    # Write default values to storage
    for name, variable in scope.all():
      self.memory[variable.offset] = variable.default_value

class MemorySnapshot:
  def __init__(self, memory: Memory):
    # self.memory = memory
    self.actual = memory.memory
    self.snapshot = list(self.actual)
    self.len = len(self.actual)

    self.temp_dirty = Bitmap() # positions in actual memory written to before flush_temp
    self.round_dirty = Bitmap() # positions in actual memory written to after flush_temp and before flush_round

    self.scope = [memory.scope]
    self.stack = [] # Storage for local scope values. Always temporary: no memory protocol applies to them

  def refresh(self):
    self.snapshot = list(self.actual)

  def store(self, offset: int, value: Any):
    if offset >= self.len:
      self.stack[offset - self.len] = value
    else:
      self.actual[offset] = value
      self.temp_dirty |= bit(offset)

  def load(self, offset: int) -> Any:
    if offset >= self.len:
      return self.stack[offset - self.len]
    else:
      if self.temp_dirty.has(offset):
        return self.actual[offset]
      else:
        return self.snapshot[offset]

  def grow_stack(self, scope):
    self.scope.append(scope)
    self.stack.extend([None]*scope.localsize())

  def shrink_stack(self):
    scope = self.scope.pop()
    del self.stack[-scope.localsize():]

  def flush_temp(self):
    assert len(self.stack) == 0 # only allowed to be called in between statement executions or expression evaluations
    
    race_conditions = self.temp_dirty & self.round_dirty
    if race_conditions:
        raise Exception("Race condition for variables %s" % str(list(self.scope[-1].get_name(offset) for offset in race_conditions.items())))

    self.round_dirty |= self.temp_dirty
    self.temp_dirty = Bitmap() # reset

  def refresh(self):
    assert len(self.stack) == 0 # only allowed to be called in between statement executions or expression evaluations

    # Probably quickest to just copy the entire list in Python
    self.snapshot = list(self.actual) # refresh
    self.round_dirty = Bitmap() # reset
