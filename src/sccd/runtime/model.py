from abc import *
from dataclasses import *
from typing import *
from sccd.runtime.statechart_syntax import *
from sccd.runtime.semantic_options import *

@dataclass
class ModelNamespace:
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

@dataclass
class StateTree:
  root: State
  states: Dict[str, State] # mapping from state "full name" (e.g. "/parallel/ortho1/a") to state
  state_list: List[State] # depth-first order
  transition_list: List[Transition] # source state depth-first order, then document order

@dataclass
class Statechart:
  tree: StateTree
  semantics: SemanticConfiguration
  datamodel: DataModel

@dataclass
class AbstractModel(ABC):
  namespace: ModelNamespace

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
