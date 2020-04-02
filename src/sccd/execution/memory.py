from typing import *
from sccd.util.bitmap import *
from sccd.util.debug import *

class Memory:
  def __init__(self, scope):
    self.scope = scope
    self.storage = [v.initial for v in scope.all_variables()]

class MemorySnapshot:
  def __init__(self, memory: Memory):
    self.actual = memory.storage
    self.snapshot = list(memory.storage)
    self.len = len(memory.storage)

    self.temp_dirty = Bitmap() # positions in actual memory written to before flush_temp
    self.round_dirty = Bitmap() # positions in actual memory written to after flush_temp and before flush_round

    self.scope = [memory.scope]
    self.stack = [] # Storage for local scope values. Always temporary: no memory protocol applies to them

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
    self.stack.extend([None]*scope.local_size())

  def shrink_stack(self):
    scope = self.scope.pop()
    if scope.local_size() > 0:
      del self.stack[-scope.local_size():]

  def flush_transition(self):
    assert len(self.stack) == 0 # only allowed to be called in between statement executions or expression evaluations
    
    race_conditions = self.temp_dirty & self.round_dirty
    if race_conditions:
      # some variable written to twice before refresh
      raise Exception("Race condition for variables %s" % str(list(self.scope[-1].get_name(offset) for offset in race_conditions.items())))

    self.round_dirty |= self.temp_dirty
    self.temp_dirty = Bitmap() # reset

  def flush_round(self):
    assert len(self.stack) == 0 # only allowed to be called in between statement executions or expression evaluations
    assert not self.temp_dirty # only allowed to be called right after flush_temp

    # Probably quickest to just copy the entire list in Python
    self.snapshot = list(self.actual) # refresh
    self.round_dirty = Bitmap() # reset
