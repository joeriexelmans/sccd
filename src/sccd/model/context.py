# from dataclasses import *
from typing import *
from sccd.syntax.expression import *
from sccd.util.namespace import *
from sccd.util.duration import *

# @dataclass
class Context:
  def __init__(self):
    self.events = Namespace()
    self.inports = Namespace()
    self.outports = Namespace()
    self.durations: List[DurationLiteral] = []

    # The smallest unit for all durations in the model
    self.delta: Optional[Duration] = None

  def _conv(self):
    for d in self.durations:
      if d.original % self.delta != Duration(0):
        print("Warning: Duration %s cannot be represented by delta %s" % (str(d.original), str(self.delta)))
      d.converted = d.original // self.delta

  def convert_durations_fixed_delta(self, delta: Duration):
    self.delta = delta
    self._conv()
    
  def convert_durations_auto_delta(self):
    self.delta = gcd(*(d.original for d in self.durations))
    self._conv()

  def assert_ready(self):
    if self.delta is None:
      raise Exception("Context not ready: durations not yet converted.")