from typing import *
from sccd.util.bitmap import *
from sccd.util.debug import *

class Memory:
  def __init__(self, scope):
    self.storage = [None] * scope.size()
    self.dirty = Bitmap(0)

    # Write default values to storage
    for name, variable in scope.all():
      self.storage[variable.offset] = variable.default_value

    self.dirty_storage = list(self.storage)

  def store(self, offset: int, value: Any):
    # Grow storage if needed
    if offset >= len(self.storage):
      n = offset-len(self.storage)+1
      self.storage.extend([None]*n)
      self.dirty_storage.extend([None]*n)

    offset_bit = bit(offset)
    if self.dirty & offset_bit:
      print_debug("Warning: Race condition at offset %d" % offset)
    self.dirty_storage[offset] = value
    self.dirty |= offset_bit

  def load(self, offset: int) -> Any:
    return self.storage[offset]

  def rotate(self):
    if self.dirty:
      self.storage = self.dirty_storage # move list
      self.dirty_storage = list(self.storage) # copy list
      self.dirty = Bitmap(0)