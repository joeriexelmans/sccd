from dataclasses import dataclass
from numbers import Real # superclass for 'int' and 'float'
from sccd.util.duration import *

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

# A simple "chrono" timer, using a configurable time function to measure wall-clock time passed since its start,
# returning elapsed times in a configurable fixed unit, efficiently.
class Timer:
    def __init__(self, impl: TimeImplementation, unit: Duration):
        self.impl = impl
        self.unit = unit
        self.paused_at = 0
        self.started_at = None
        self.convert = lambda x: int(get_conversion_f(
            from_unit=self.impl.time_unit, to_unit=unit)(x))
        self.paused = True

    # Start (if not paused) or continue timer (if paused)
    def start(self):
        self.started_at = self.convert(self.impl.get_time()) + self.paused_at
        self.paused = False

    def pause(self):
        self.paused_at = self.now()
        self.paused = True

    # The number returned will be the wall-clock time elapsed since the call to start(),
    # divided by the 'unit' passed to the constructor of this object, minus of course
    # the time elapsed while the timer was 'paused'.
    def now(self) -> int:
        assert not self.paused
        return self.convert(self.impl.get_time()) - self.started_at

    def is_paused(self) -> bool:
        return self.paused

    # Note: We could add a reset() method, but we simply don't need it for our purposes :)
