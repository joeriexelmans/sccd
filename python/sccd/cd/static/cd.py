from abc import *
from dataclasses import *
from typing import *
from sccd.statechart.static.statechart import *
from sccd.statechart.static.globals import *

@dataclass
class AbstractCD(ABC, Visitable):
  globals: Globals

  @abstractmethod
  def get_default_class(self) -> Statechart:
    pass

  # Get the "model delta", i.e. the smallest possible duration representable.
  def get_delta(self) -> Duration:
    return self.globals.delta

@dataclass
class CD(AbstractCD):
  classes: Dict[str, Statechart]
  default_class: Optional[str]

  def get_default_class(self) -> Statechart:
    return self.classes[self.default_class]

@dataclass
class SingleInstanceCD(AbstractCD):
  statechart: Statechart

  def get_default_class(self) -> Statechart:
    return self.statechart

  def print(self):
    print("%d states. %d transitions." % (len(self.statechart.tree.state_list), len(self.statechart.tree.transition_list)))
    print("Internal events:")
    for event_id in bm_items(self.statechart.internal_events):
      print("  %s" % self.globals.events.get_name(event_id))
    for outport in self.globals.outports.names:
      print("Outport \"%s\" events:" % outport)
      for event_name, port in self.statechart.event_outport.items():
        if port == outport:
          print("  %s" % event_name)
