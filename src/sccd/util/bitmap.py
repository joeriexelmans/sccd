from typing import *
from functools import reduce
import math

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
    v = reduce(lambda x,y: x|2**y, iterable, 0) # iterable
    return super(cls, cls).__new__(cls, v)

  def __repr__(self):
    return "Bitmap("+format(self, 'b')+")"

  def __str__(self):
    return self.__repr__()

  def __or__(self, other):
    return self.__class__(super().__or__(other))

  def __and__(self, other):
    return self.__class__(super().__and__(other))

  def __invert__(self):
    return self.__class__(super().__invert__())

  def has(self, pos):
    return self & 2**pos

  def has_all(self, bitmap):
    return (self | bitmap) == self

  # pos of first set bit
  def first_bit_pos(self):
    return math.floor(math.log2(x & -x))

  def items(self) -> Iterable[int]:
    pos = 0
    while 2**pos <= self:
      if self & 2**pos:
        yield pos
      pos += 1

# Create a bitmap with a single bit set.
def bit(pos):
  return Bitmap(2 ** pos)
