from functools import reduce
import math

class Bitmap(int):
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

  def set(self, pos):
    return self.__or__(2**pos)

  def unset(self, pos):
    return self.__and__(~2**pos)

  def has(self, pos):
    return self & 2**pos

  def has_all(self, bitmap):
    return (self | bitmap) == self

  # pos of first set bit
  def first_bit_pos(self):
    return math.floor(math.log2(x & -x))


def Bit(pos):
  return Bitmap(2 ** pos)
