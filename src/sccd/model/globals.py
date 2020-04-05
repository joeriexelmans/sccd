# from dataclasses import *
import termcolor
from typing import *
from sccd.action_lang.static.expression import *
from sccd.util.namespace import *
from sccd.util.duration import *
from sccd.util.debug import *

# @dataclass
class Globals:
  # max_delta: upper bound on model delta
  def __init__(self, fixed_delta: Optional[Duration] = duration(100, Microsecond)):
    self.fixed_delta = fixed_delta

    self.events = Namespace()
    self.inports = Namespace()
    self.outports = Namespace()
    self.durations: List[Duration] = []

    # The smallest unit for all durations in the model.
    # Calculated after all expressions have been parsed, based on all DurationLiterals.
    self.delta: Optional[Duration] = None

  def process_durations(self):
    self.delta = gcd(*self.durations)

    # self.delta will be duration(0) now if there are no durations in the model, or all durations are 0.

    # Ensure delta not too big
    if self.fixed_delta:
      if duration(0) < self.delta < self.fixed_delta:
        raise Exception("Model contains duration deltas (smallest = %s) not representable with fixed delta of %s." % (str(self.delta), str(self.fixed_delta)))
      else:
        self.delta = self.fixed_delta

    # if self.delta == duration(0):
    #   print_debug(termcolor.colored("Warning: model delta is 0: Model does not have any notion of time.", 'yellow'))
    # else:
    #   pass
      # # Convert all DurationLiterals to model delta
      # for d in self.durations:
      #   # The following error is impossible: (i think)
      #   # if d.original % self.delta != duration(0):
      #   #   raise Exception("Duration %s cannot be represented by delta %s" % (str(d.original), str(self.delta)))
      #   d.converted = d.original // self.delta

  def assert_ready(self):
    if self.delta is None:
      raise Exception("Globals not ready: durations not yet processed.")
