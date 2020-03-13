from dataclasses import *
from typing import *

@dataclass
class Namespace:
  def __init__(self):
    self.events: Dict[str, int] = {}
    self.inports: List[str] = []
    self.outports: List[str] = []

  def assign_event_id(self, name: str) -> int:
    return self.events.setdefault(name, len(self.events))

  def get_event_id(self, name: str) -> int:
    return self.events[name]

  def add_inport(self, port: str):
    if port not in self.inports:
      self.inports.append(port)

  def add_outport(self, port: str):
    if port not in self.outports:
      self.outports.append(port)
