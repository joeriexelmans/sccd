from enum import *
from abc import *
from dataclasses import *
from typing import *
import math
import functools

class _Unit:
  __slots__ = ["notation", "larger", "conv_dict"]
  def __init__(self, notation: str, larger: Optional[Tuple[int, '_Unit']] = None):
    self.notation = notation
    self.larger = larger

    # Pre-calculate conversions to all larger units
    self.conv_dict = {}
    rel_size = 1
    larger = (1, self)
    while larger:
      rel_size *= larger[0]
      unit = larger[1]
      self.conv_dict[unit] = rel_size
      larger = unit.larger

Hour = _Unit("h")
Minute = _Unit("m", (60, Hour))
Second = _Unit("s", (60, Minute))
Millisecond = _Unit("ms", (1000, Second))
Microsecond = _Unit("µs", (1000, Millisecond))
Nanosecond = _Unit("ns", (1000, Microsecond))
PicoSecond = _Unit("ps", (1000, Nanosecond))
FemtoSecond = _Unit("fs", (1000, PicoSecond))

class Duration(ABC):
  def __repr__(self):
    return "Duration("+self.__str__()+")"

  @abstractmethod
  def __str__(self):
    pass

  @abstractmethod
  def __eq__(self, other):
    pass

  @abstractmethod
  def __add__(self, other):
    pass

  @abstractmethod
  def __sub__(self, other):
    pass

  @abstractmethod
  def __neg__(self):
    pass

  @abstractmethod
  def __mul__(self):
    pass

  @abstractmethod
  def __rmul__(self):
    pass

  @abstractmethod
  def __bool__(self):
    pass

  def __floordiv__(self, other: 'Duration') -> int:
    if other is _zero:
      raise ZeroDivisionError("duration floordiv by zero duration")
    self_val, other_val, _ = _same_unit(self, other)
    return self_val // other_val

  def __mod__(self, other: 'Duration'):
      self_val, other_val, unit = _same_unit(self, other)
      new_val = self_val % other_val
      return _duration_no_checks(new_val, unit)

  def __lt__(self, other):
    self_val, other_val, unit = _same_unit(self, other)
    return self_val < other_val

class _ZeroDuration(Duration):
  def __str__(self):
    return '0 d'

  def __eq__(self, other):
    return self is other

  def __add__(self, other):
    return other

  def __sub__(self, other):
    return other.__neg__()

  def __neg__(self):
    return self

  def __mul__(self, other: int) -> Duration:
    return self

  __rmul__ = __mul__

  def __floordiv__(self, other) -> int:
    if isinstance(other, Duration):
      return Duration.__floordiv__(self, other)
    elif isinstance(other, int):
      if other == 0:
        raise ZeroDivisionError("duration floordiv by zero")
      else:
        return _ZeroDuration
    else:
      raise TypeError("cannot floordiv duration by %s" % type(other))

  def __mod__(self, other):
    if isinstance(other, Duration):
      return Duration.__mod__(self, other)
    elif isinstance(other, int):
      if other == 0:
        raise ZeroDivisionError("duration modulo by zero")
      else:
        return _ZeroDuration
    else:
      raise TypeError("cannot modulo duration by %s" % type(other))

  def __bool__(self):
    return False

_zero = _ZeroDuration() # Singleton. Only place the constructor should be called.

# Only exported way to construct a Duration object
def duration(val: int, unit: Optional[_Unit] = None) -> Duration:
  if unit is None:
    if val != 0:
      raise Exception("Duration: Non-zero value should have unit")
    else:
      return _zero
  else:
    if val == 0:
      raise Exception("Duration: Zero value should have pseudo-unit 'd'")
    else:
      return _NonZeroDuration(val, unit)

def _duration_no_checks(val: int, unit: _Unit) -> Duration:
  if val == 0:
    return _zero
  else:
    return _NonZeroDuration(val, unit)

class _NonZeroDuration(Duration):
  __slots__ = ["val", "unit"]
  def __init__(self, val: int, unit: _Unit = None):
    self.val = val
    self.unit = unit

    # Use largest possible unit without losing precision
    while self.unit.larger:
      factor, next_unit = self.unit.larger
      if self.val % factor != 0:
        break
      self.val //= factor
      self.unit = next_unit

  def __str__(self):
    return str(self.val)+' '+self.unit.notation

  def __eq__(self, other):
    if other is _zero:
      return False
    return self.val == other.val and self.unit is other.unit

  def __add__(self, other):
    if other is _zero:
      return self
    self_val, other_val, unit = _same_unit(self, other)
    return _duration_no_checks(self_val + other_val, unit)

  def __sub__(self, other):
    if other is _zero:
      return self
    self_val, other_val, unit = _same_unit(self, other)
    return _duration_no_checks(self_val - other_val, unit)

  def __neg__(self):
    return _NonZeroDuration(-self.val, self.unit)

  def __mul__(self, other: int) -> Duration:
    if other == 0:
      return _zero
    return _NonZeroDuration(self.val * other, self.unit)

  __rmul__ = __mul__

  def __floordiv__(self, other) -> int:
    if isinstance(other, Duration):
      return Duration.__floordiv__(self, other)
    elif isinstance(other, int):
      if other == 0:
        raise ZeroDivisionError("duration floordiv by zero")
      else:
        new_val = self.val // other
        if new_val == 0:
          return _zero
        else:
          return _NonZeroDuration(self.val, self.unit)
    else:
      raise TypeError("cannot floordiv duration by %s" % type(other))

  def __mod__(self, other):
    if isinstance(other, Duration):
      return Duration.__mod__(self, other)
    elif isinstance(other, int):
      return _duration_no_checks(self.val % other, self.unit)
    else:
      raise TypeError("cannot modulo duration by %s" % type(other))

  def __bool__(self):
    return True

# Convert both durations to the largest unit among them.
def _same_unit(x: Duration, y: Duration) -> Tuple[int, int, _Unit]:
  if x is _zero:
    if y is _zero:
      return (0, 0, None)
    else:
      return (0, y.val, y.unit)
  if y is _zero:
    return (x.val, 0, x.unit)

  try:
    factor = x.unit.conv_dict[y.unit]
    return (x.val, y.val * factor, x.unit)
  except KeyError:
    factor = y.unit.conv_dict[x.unit]
    return (x.val * factor, y.val, y.unit)

def gcd_pair(x: Duration, y: Duration) -> Duration:
  x_conv, y_conv, unit = _same_unit(x, y)
  gcd = math.gcd(x_conv, y_conv)
  return _duration_no_checks(gcd, unit)

def gcd(*iterable: Iterable[Duration]) -> Duration:
  return functools.reduce(gcd_pair, iterable, _zero)

# Useful for efficiently converting many values from some fixed unit to some other fixed unit.
def get_conversion_f(from_unit: Duration, to_unit: Duration) -> Callable[[int], int]:
  if from_unit is _zero or to_unit is _zero:
    raise Exception("Cannot convert between zero-duration units")
    
  if from_unit > to_unit:
    factor = from_unit // to_unit
    return lambda x: x * factor
  else:
    factor = to_unit // from_unit
    return lambda x: x // factor

def get_conversion_f_float(from_unit: Duration, to_unit: Duration) -> Callable[[Union[int,float]], Union[int,float]]:
  if from_unit is _zero or to_unit is _zero:
    raise Exception("Cannot convert between zero-duration units")
    
  if from_unit > to_unit:
    factor = from_unit // to_unit
    return lambda x: x * factor
  else:
    factor = to_unit // from_unit
    return lambda x: x / factor
