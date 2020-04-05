from abc import *
from dataclasses import *
from typing import *
from sccd.statechart.static.statechart import *
from sccd.model.globals import *

@dataclass
class AbstractModel(ABC):
  globals: Globals

  @abstractmethod
  def get_default_class(self) -> Statechart:
    pass

@dataclass
class MultiInstanceModel(AbstractModel):
  classes: Dict[str, Statechart]
  default_class: Optional[str]

  def get_default_class(self) -> Statechart:
    return self.classes[self.default_class]

@dataclass
class SingleInstanceModel(AbstractModel):
  statechart: Statechart

  def get_default_class(self) -> Statechart:
    return self.statechart
