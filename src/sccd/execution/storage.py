from typing import *
from sccd.util.bitmap import *
from sccd.util.debug import *

class Storage:
  def __init__(self, scope):
    self.scope = scope
    self.storage = [None] * scope.size()

    # Write default values to storage
    for name, variable in scope.all():
      self.storage[variable.offset] = variable.default_value

class DirtyStorage:
  def __init__(self, storage: Storage):
    self.storage = storage

    self.clean = storage.storage

    # Dirty storage: Values copied to clean storage when rotated.
    self.dirty = list(self.clean)

    self.temp_dirty = Bitmap() # dirty values written by current transition
    self.round_dirty = Bitmap()

    # Storage for local scope values. No values ever copied from here to 'clean' storage
    self.temp_stack = [None]*1024


  def store(self, offset: int, value: Any):
    if offset >= len(self.clean):
      self.temp_stack[offset - len(self.clean)] = value
    else:
      self.dirty[offset] = value
      self.temp_dirty |= bit(offset)

  def load(self, offset: int) -> Any:
    if offset >= len(self.clean):
      return self.temp_stack[offset - len(self.clean)]
    else:
      if self.temp_dirty.has(offset):
        return self.dirty[offset]
      else:
        return self.clean[offset]

  def flush_temp(self):
    race_conditions = self.temp_dirty & self.round_dirty
    if race_conditions:
        raise Exception("Race condition for variables %s" % str(list(self.storage.scope.name(offset) for offset in race_conditions.items())))

    self.round_dirty |= self.temp_dirty
    self.temp_dirty = Bitmap()

  def flush_round(self):
    for i in self.round_dirty.items():
      self.clean[i] = self.dirty[i] # copy dirty values to clean storage
    self.round_dirty = Bitmap()
