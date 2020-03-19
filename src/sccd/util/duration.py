from enum import *
from dataclasses import *
from typing import *
import math
import functools

@dataclass
class Unit:
  notation: str
  relative_size: int
  larger: Optional[Tuple[Any, int]] = None
  # smaller: Optional[Tuple[Any, int]] = None

  def __eq__(self, other):
    return self is other

FemtoSecond = Unit("fs", 1)
PicoSecond = Unit("ps", 1000)
Nanosecond = Unit("ns", 1000000)
Microsecond = Unit("µs", 1000000000)
Millisecond = Unit("ms", 1000000000000)
Second = Unit("s", 1000000000000000)
Minute = Unit("m", 60000000000000000)
Hour = Unit("h", 3600000000000000000)
Day = Unit("D", 86400000000000000000)

FemtoSecond.larger = (PicoSecond, 1000)
PicoSecond.larger = (Nanosecond, 1000)
Nanosecond.larger = (Microsecond, 1000)
Microsecond.larger = (Millisecond, 1000)
Millisecond.larger = (Second, 1000)
Second.larger = (Minute, 60)
Minute.larger = (Hour, 60)
Hour.larger = (Day, 24)

# Day.smaller = (Hour, 24)
# Hour.smaller = (Minute, 60)
# Minute.smaller = (Second, 60)
# Second.smaller = (Millisecond, 1000)
# Millisecond.smaller = (Microsecond, 1000)
# Microsecond.smaller = (Nanosecond, 1000)
# Nanosecond.smaller = (PicoSecond, 1000)
# PicoSecond.smaller = (FemtoSecond, 1000)


# @dataclass
class Duration:
  def __init__(self, val: int, unit: Unit = None):
    self.val = val
    self.unit = unit

    if self.val != 0 and self.unit is None:
      raise Exception("Duration: Non-zero value should have unit")
    # Zero-durations are treated a bit special
    if self.val == 0 and self.unit is not None:
      raise Exception("Duration: Zero value should not have unit")

  # Can only convert to smaller units.
  # Returns new Duration.
  def convert(self, unit: Unit):
    if self.unit is None:
      return self

    # Precondition
    assert self.unit.relative_size >= unit.relative_size
    factor = self.unit.relative_size // unit.relative_size
    return Duration(self.val * factor, unit)

  # Convert Duration to the largest possible unit.
  # Returns new Duration.
  def normalize(self):
    if self.unit is None:
      return self

    val = self.val
    unit = self.unit
    next_unit, factor = unit.larger
    while val % factor == 0:
      val //= factor
      unit = next_unit
      next_unit, factor = unit.larger
    return Duration(val, unit)

  def __str__(self):
    if self.unit is None:
      return '0'
    return str(self.val)+' '+self.unit.notation

  def __repr__(self):
    return "Duration("+self.__str__()+")"

  def __eq__(self, other):
    return self.val == other.val and self.unit is other.unit

  def __mul__(self, other):
    new_val = self.val * other
    if new_val == 0:
      return Duration(0)
    else:
      return Duration(new_val, self.unit)

  # Commutativity
  __rmul__ = __mul__

  def __floordiv__(self, other):
    # if isinstance(other, Duration):
      self_conv, other_conv = same_unit(self, other)
      return self_conv.val // other_conv.val
    # else:
      # return Duration(self.val//other, self.unit)


  def __mod__(self, other):
    # if isinstance(other, Duration):
      self_conv, other_conv = same_unit(self, other)
      new_val = self_conv.val % other_conv.val
      if new_val == 0:
        return Duration(0)
      else:
        return Duration(new_val, self_conv.unit)
    # else:
      # return Duration(self.val%other, self.unit)

  def __lt__(self, other):
    self_conv, other_conv = same_unit(self, other)
    return self_conv.val < other_conv.val

def same_unit(x: Duration, y: Duration) -> Tuple[Duration, Duration]:
  if x.unit.relative_size >= y.unit.relative_size:
    x_conv = x.convert(y.unit)
    y_conv = y
  else:
    x_conv = x
    y_conv = y.convert(x.unit)
  return (x_conv, y_conv)

def gcd_pair(x: Duration, y: Duration) -> Duration:
  if x.unit is None:
    return y
  if y.unit is None:
    return x

  x_conv, y_conv = same_unit(x, y)
  gcd = math.gcd(x_conv.val, y_conv.val)
  return Duration(gcd, x_conv.unit).normalize()

def gcd(*iterable) -> Duration:
  return functools.reduce(gcd_pair, iterable, Duration(0))
