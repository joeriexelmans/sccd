from dataclasses import *
from typing import *
from sccd.syntax.expression import *

class Namespace:
  def __init__(self):
    self.names: Dict[str, int] = {}

  def assign_id(self, name: str) -> int:
    return self.names.setdefault(name, len(self.names))

  def get_id(self, name: str) -> int:
    return self.names[name]

# @dataclass
class Context:
  def __init__(self):
    self.events = Namespace()
    self.inports = Namespace()
    self.outports = Namespace()
    self.durations: List[DurationLiteral] = []