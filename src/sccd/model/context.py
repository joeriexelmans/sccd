# from dataclasses import *
from typing import *
from sccd.syntax.expression import *
from sccd.util.namespace import *
from sccd.util.duration import *

# @dataclass
class Context:
  # max_delta: upper bound on model delta
  def __init__(self, fixed_delta: Optional[Duration] = Duration(100, Microsecond)):
    self.fixed_delta = fixed_delta

    self.events = Namespace()
    self.inports = Namespace()
    self.outports = Namespace()
    self.durations: List[DurationLiteral] = []

    # The smallest unit for all durations in the model.
    # Calculated after all expressions have been parsed, based on all DurationLiterals.
    self.delta: Optional[Duration] = None

  # Convert all DurationLiterals to model delta
  def _conv(self):
    for d in self.durations:
      # The following error is impossible: (i think)
      # if d.original % self.delta != Duration(0):
      #   raise Exception("Duration %s cannot be represented by delta %s" % (str(d.original), str(self.delta)))
      d.converted = d.original // self.delta

  def process_durations(self):
    self.delta = gcd(*(d.original for d in self.durations))

    # Ensure delta not too big
    if self.fixed_delta:
      if self.delta < self.fixed_delta:
        raise Exception("Model contains duration deltas (smallest = %s) not representable with fixed delta of %s." % (str(self.delta), str(self.fixed_delta)))
      else:
        self.delta = self.fixed_delta

    self._conv()

  def assert_ready(self):
    if self.delta is None:
      raise Exception("Context not ready: durations not yet processed.")