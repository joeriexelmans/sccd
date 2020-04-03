from typing import *
from sccd.util.bitmap import *
from sccd.util.debug import *

class Memory:
  def __init__(self, scope):
    self.scope = scope
    self.storage = [None]*scope.total_size()

class MemorySnapshot:
  def __init__(self, memory: Memory):
    self.actual = memory.storage
    self.snapshot = list(memory.storage)
    self.len = len(memory.storage)

    self.trans_dirty = Bitmap() # positions in actual memory written to before flush_transition
    self.round_dirty = Bitmap() # positions in actual memory written to after flush_temp and before flush_round

    self.local_storage: Dict[Scope, List[List[Any]]] = {}

  def store(self, scope, offset: int, value: Any):
    try:
      scope_stack = self.local_storage[scope]
      scope_stack[-1][offset] = value
    except KeyError:
      self.actual[offset] = value
      self.trans_dirty |= bit(offset)

  def load(self, scope, offset: int) -> Any:
    try:
      scope_stack = self.local_storage[scope]
      return scope_stack[-1][offset]
    except KeyError:
      if self.trans_dirty.has(offset):
        return self.actual[offset]
      else:
        return self.snapshot[offset]

  def push_local_scope(self, scope):
    scope_stack = self.local_storage.setdefault(scope, [])
    scope_stack.append([None]*scope.local_size()) # append stack frame

  def pop_local_scope(self, scope):
    scope_stack = self.local_storage[scope]
    scope_stack.pop() # pop stack frame

  def flush_transition(self):  
    race_conditions = self.trans_dirty & self.round_dirty
    if race_conditions:
      variables = list(self.scope[-1].all_variables())
      # some variable written to twice before refresh
      raise Exception("Race condition for variables %s" % str(list(variables[offset].name for offset in race_conditions.items())))

    self.round_dirty |= self.trans_dirty
    self.trans_dirty = Bitmap() # reset

  def flush_round(self):
    assert not self.trans_dirty # only allowed to be called right after flush_temp

    # Probably quickest to just copy the entire list in Python
    self.snapshot = list(self.actual) # refresh
    self.round_dirty = Bitmap() # reset
