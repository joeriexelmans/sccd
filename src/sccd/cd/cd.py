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
