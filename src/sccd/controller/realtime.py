from abc import *
from sccd.controller.controller import *
from numbers import Real # superclass for 'int' and 'float'

# The only requirement for a TimeImplementation is that the diffs between get_time call results are real durations of a non-complex number type (int, float).
@dataclass
class TimeImplementation:
    time_unit: Duration
    get_time: Callable[[], Real]

# This is the most accurate time function in Python 3.6
from time import perf_counter
PerfCounterTime = TimeImplementation(
    time_unit=duration(1, Second),
    get_time=perf_counter) # returns float

DefaultTimeImplementation = PerfCounterTime

# Python >= 3.7 has a better time function
import sys
if sys.version_info.minor >= 7:
    from time import perf_counter_ns
    PerfCounterNSTime = TimeImplementation(
        time_unit=duration(1, Nanosecond),
        get_time=perf_counter_ns) # returns int
    DefaultTimeImplementation = PerfCounterNSTime


class Timer:
    def __init__(self, impl: TimeImplementation, unit: Duration):
        self.impl = impl
        self.unit = unit
        self.paused_at = 0
        self.started_at = None
        self.convert = lambda x: int(get_conversion_f(
            from_unit=self.impl.time_unit, to_unit=unit)(x))
        self.paused = True

    def start(self):
        self.started_at = self.convert(self.impl.get_time()) + self.paused_at
        self.paused = False

    def pause(self):
        self.paused_at = self.now()
        self.paused = True

    # Only call when not paused!
    def now(self) -> int:
        return self.convert(self.impl.get_time()) - self.started_at

    def is_paused(self):
        return self.paused
