from typing import *
from functools import reduce
from sccd.util.debug import *

if DEBUG:
  # Bitmap inherits 'int' and is therefore immutable.
  # Methods that return a Bitmap return a new bitmap and leave the arguments untouched.
  # To change a bitmap, use an assignment operator ('=', '|=', '&=', ...)
  class Bitmap(int):
    # Create from int
    def __new__(cls, value=0, *args, **kwargs):
      return super(cls, cls).__new__(cls, value)

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
else:
  Bitmap = int # Much faster than our overrides! Only thing we miss out on is pretty printing as a binary string


# Create a bitmap with a single bit set.
def bit(pos):
  return Bitmap(1 << pos)


# The following functions are not methods of Bitmap so that they also work on integers:

# Non-member function variants so they also work on integers:
def bm_from_list(iterable):
  v = reduce(lambda x,y: x|1<<y, iterable, 0) # iterable
  return Bitmap(v)

def bm_has(self, pos):
  return self & 1 << pos

def bm_has_all(self, bitmap):
  return (self | bitmap) == self

def bm_lowest_bit(self) -> int:
  low = self & -self # only the lowest bit set
  pos = -1
  while low:
    low >>= 1
    pos += 1
  return pos

def bm_highest_bit(self) -> int:
  pos = -1
  while self:
    self >>= 1
    pos += 1
  return pos

def bm_items(self) -> Iterable[int]:
  pos = 0
  while self > 0:
    if (self >> 1) << 1 != self:
      yield pos
    pos += 1
    self >>= 1

# Takes 2 iterations over our bitmap, one for highest_bit,
# and then to find the rest of the bits.
def bm_reverse_items(self) -> Iterable[int]:
  pos = bm_highest_bit(self)
  if pos >= 0:
    yield pos
  pos -= 1
  while pos >= 0:
    high = 1 << pos
    if self & high:
      yield pos
    self -= high # unset high bit
    pos -= 1
