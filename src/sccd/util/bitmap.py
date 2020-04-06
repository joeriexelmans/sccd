from typing import *
from functools import reduce

# Bitmap inherits 'int' and is therefore immutable.
# Methods that return a Bitmap return a new bitmap and leave the arguments untouched.
# To change a bitmap, use an assignment operator ('=', '|=', '&=', ...)
class Bitmap(int):
  # Create from int
  def __new__(cls, value=0, *args, **kwargs):
    return super(cls, cls).__new__(cls, value)

  # iterable: positions of bits to set.
  @classmethod
  def from_list(cls, iterable):
    v = reduce(lambda x,y: x|1<<y, iterable, 0) # iterable
    return super(cls, cls).__new__(cls, v)

  def __repr__(self):
    return "Bitmap('"+format(self, 'b')+"')"

  def __str__(self):
    return self.__repr__()

  def __or__(self, other):
    return self.__class__(super().__or__(other))

  def __and__(self, other):
    return self.__class__(super().__and__(other))

  def __invert__(self):
    return self.__class__(super().__invert__())

  def __neg__(self):
    return self.__class__(super().__neg__())

  def has(self, pos):
    return self & 1 << pos

  def has_all(self, bitmap):
    return (self | bitmap) == self

  def lowest_bit(self) -> int:
    low = self & -self # only the lowest bit set
    pos = -1
    while low:
      low >>= 1
      pos += 1
    return pos

  def highest_bit(self) -> int:
    pos = -1
    while self:
      self >>= 1
      pos += 1
    return pos

  # Takes 1 iteration over our bitmap
  def items(self) -> Iterable[int]:
    pos = 0
    while self > 0:
      if (self >> 1) << 1 != self:
        yield pos
      pos += 1
      self >>= 1

  # Takes 2 iterations over our bitmap, one for highest_bit,
  # and then to find the rest of the bits.
  def reverse_items(self) -> Iterable[int]:
    pos = self.highest_bit()
    if pos >= 0:
      yield pos
    pos -= 1
    while pos >= 0:
      high = 1 << pos
      if self & high:
        yield pos
      self -= high # unset high bit
      pos -= 1

# Create a bitmap with a single bit set.
def bit(pos):
  return Bitmap(1 << pos)
