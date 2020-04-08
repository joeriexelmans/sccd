# from dataclasses import *
import termcolor
from typing import *
from sccd.action_lang.static.expression import *
from sccd.util.namespace import *
from sccd.util.duration import *
from sccd.util.debug import *

# @dataclass
class Globals:
  def __init__(self):
    self.events = Namespace()
    self.inports = Namespace()
    self.outports = Namespace()
    self.durations: List[Duration] = []

    # The smallest unit for all durations in the model.
    # Calculated after all expressions have been parsed, based on all DurationLiterals.
    self.delta: Optional[Duration] = None

  # delta: if set, this will be the model delta. otherwise, model delta will be the GCD of all durations registered.
  def set_delta(self, delta: Optional[Duration]):
    gcd_delta = gcd(*self.durations)

    # Ensure delta not too big
    if delta:
      if duration(0) < gcd_delta < delta:
        raise Exception("Model contains duration deltas (smallest = %s) not representable with delta of %s." % (str(self.delta), str(delta)))
      else:
        self.delta = delta
    else:
      self.delta = gcd_delta

  def assert_ready(self):
    if self.delta is None:
      raise Exception("Globals not ready: durations not yet processed.")
