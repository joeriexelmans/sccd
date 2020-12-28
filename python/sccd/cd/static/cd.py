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
    # if self.statechart.in_events:
    #   print("Input events:")
    #   for event_name in self.statechart.in_events:
    #     print("  %s" % event_name)
    # if len(self.statechart.out_events) > 0:
    #   print("Output events:")
    #   for event_name in self.statechart.out_events:
    #     print("  %s" % event_name)
    # if self.statechart.internal_events:
    #   print("Internal events:")
    #   for event_name in self.statechart.internal_events:
    #     print("  %s" % event_name)
    print()