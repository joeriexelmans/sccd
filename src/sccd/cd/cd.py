from abc import *
from dataclasses import *
from typing import *
from sccd.statechart.static.statechart import *
from sccd.cd.globals import *

@dataclass
class AbstractCD(ABC):
  globals: Globals

  @abstractmethod
  def get_default_class(self) -> Statechart:
    pass

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
    for inport, events in self.statechart.inport_events.items():
      print("Inport \"%s\" events:" % inport)
      for event_id in events:
        print("  %s" % self.globals.events.get_name(event_id))
    print()
    for outport in self.globals.outports.names:
      print("Outport \"%s\" events:" % outport)
      for event_name, port in self.statechart.event_outport.items():
        if port == outport:
          print("  %s" % event_name)
    print()
    print("Internal events:")
    for event_id in self.statechart.internal_events.items():
      print("  %s" % self.globals.events.get_name(event_id))
    print()
    print("All event triggers:")
    for event_id in self.statechart.events.items():
      print("  %s" % self.globals.events.get_name(event_id))
    print()