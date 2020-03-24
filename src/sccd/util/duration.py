from enum import *
from abc import *
from dataclasses import *
from typing import *
import math
import functools

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

class Duration(ABC):
  def __repr__(self):
    return "Duration("+self.__str__()+")"

  @abstractmethod
  def __str__(self):
    pass

  @abstractmethod
  def __eq__(self):
    pass

  @abstractmethod
  def __mul__(self):
    pass

  def __floordiv__(self, other: 'Duration') -> int:
    if other is _zero:
      raise ZeroDivisionError("duration floordiv by zero duration")
    self_conv, other_conv, _ = _same_unit(self, other)
    return self_conv // other_conv

  def __mod__(self, other):
      self_conv, other_conv, unit = _same_unit(self, other)
      new_val = self_conv % other_conv
      if new_val == 0:
        return _zero
      else:
        return _NonZeroDuration(new_val, unit)

  def __lt__(self, other):
    self_conv, other_conv = _same_unit(self, other)
    return self_conv.val < other_conv.val

class _ZeroDuration(Duration):
  def _convert(self, unit: _Unit) -> int:
    return 0

  def __str__(self):
    return '0'

  def __eq__(self, other):
    return self is other

  def __mul__(self, other: int) -> Duration:
    return self

  # Commutativity
  __rmul__ = __mul__

_zero = _ZeroDuration() # Singleton. Only place the constructor should be called.

def duration(val: int, unit: Optional[_Unit] = None) -> Duration:
  if unit is None:
    if val != 0:
      raise Exception("Duration: Non-zero value should have unit")
    else:
      return _zero
  else:
    if val == 0:
      raise Exception("Duration: Zero value should not have unit")
    else:
      return _NonZeroDuration(val, unit)

# @dataclass
class _NonZeroDuration(Duration):
  def __init__(self, val: int, unit: _Unit = None):
    self.val = val
    self.unit = unit

    while self.unit.larger:
      next_unit, factor = self.unit.larger
      if self.val % factor != 0:
        break
      self.val //= factor
      self.unit = next_unit

  # Can only convert to smaller units.
  # Returns new Duration.
  def _convert(self, unit: _Unit) -> int:
    # Precondition
    assert self.unit.relative_size >= unit.relative_size
    factor = self.unit.relative_size // unit.relative_size
    return self.val * factor

  def __str__(self):
    return str(self.val)+' '+self.unit.notation


  def __eq__(self, other):
    if isinstance(other, _ZeroDuration):
      return False
    return self.val == other.val and self.unit is other.unit

  def __mul__(self, other: int) -> Duration:
    if other == 0:
      return _zero
    return _NonZeroDuration(self.val * other, self.unit)

  # Commutativity
  __rmul__ = __mul__

def _same_unit(x: Duration, y: Duration) -> Tuple[int, int, _Unit]:
  if x is _zero:
    if y is _zero:
      return (0, 0, None)
    else:
      return (0, y.val, y.unit)
  if y is _zero:
    return (x.val, 0, x.unit)

  if x.unit.relative_size >= y.unit.relative_size:
    x_conv = x._convert(y.unit)
    y_conv = y.val
    unit = y.unit
  else:
    x_conv = x.val
    y_conv = y._convert(x.unit)
    unit = x.unit
  return (x_conv, y_conv, unit)

def gcd_pair(x: Duration, y: Duration) -> Duration:
  x_conv, y_conv, unit = _same_unit(x, y)
  gcd = math.gcd(x_conv, y_conv)
  return duration(gcd, unit)

def gcd(*iterable: Iterable[Duration]) -> Duration:
  return functools.reduce(gcd_pair, iterable, _zero)
