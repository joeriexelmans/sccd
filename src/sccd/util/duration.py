from enum import *
from dataclasses import *
from typing import *
import math

@dataclass
class _Unit:
  notation: str
  relative_size: int
  larger: Optional[Tuple[Any, int]] = None
  # smaller: Optional[Tuple[Any, int]] = None

  def __eq__(self, other):
    return self is other

FemtoSecond = _Unit("fs", 1)
PicoSecond = _Unit("ps", 1000)
Nanosecond = _Unit("ns", 1000000)
Microsecond = _Unit("µs", 1000000000)
Millisecond = _Unit("ms", 1000000000000)
Second = _Unit("s", 1000000000000000)
Minute = _Unit("m", 60000000000000000)
Hour = _Unit("h", 3600000000000000000)
Day = _Unit("D", 86400000000000000000)

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
  def __init__(self, val: int, unit: _Unit = None):
    self.val = val
    self.unit = unit
    if self.val != 0 and self.unit is None:
      raise Exception("Duration: Non-zero value should have unit")
    # Zero-durations are treated a bit special
    if self.val == 0 and self.unit is not None:
      raise Exception("Duration: Zero value should not have unit")

  # Can only convert to smaller units.
  # Returns new Duration.
  def convert(self, unit: _Unit):
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

def gcd_pair(x: Duration, y: Duration) -> Duration:
  if x.unit is None:
    return y
  if y.unit is None:
    return x

  if x.unit.relative_size >= y.unit.relative_size:
    x_converted = x.convert(y.unit)
    y_converted = y
  else:
    x_converted = x
    y_converted = y.convert(x.unit)
  # x_conv and y_conv are now the same unit
  gcd = math.gcd(x_converted.val, y_converted.val)
  return Duration(gcd, x_converted.unit).normalize()

def gcd(*iterable) -> Duration:
  g = None
  for d in iterable:
    if g is None:
      g = d
    else:
      g = gcd_pair(g, d)
  return g