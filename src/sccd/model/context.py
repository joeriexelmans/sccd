# from dataclasses import *
from typing import *
from sccd.syntax.expression import *
from sccd.util.namespace import *

# @dataclass
class Context:
  def __init__(self):
    self.events = Namespace()
    self.inports = Namespace()
    self.outports = Namespace()
    self.durations: List[DurationLiteral] = []