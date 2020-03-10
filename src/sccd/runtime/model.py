from dataclasses import *
from typing import *
from sccd.runtime.statechart_syntax import *
from sccd.runtime.semantic_options import *

# Mapping from event name to event ID
class EventNamespace:
  def __init__(self):
    self.mapping: Dict[str, int] = {}

  def assign_id(self, event: str) -> int:
    return self.mapping.setdefault(event, len(self.mapping))

  def get_id(self, event: str) -> int:
    return self.mapping[event]

@dataclass
class Statechart:
  root: State
  states: Dict[str, State] # mapping from state "full name" (e.g. "/parallel/ortho1/a") to state
  state_list: List[State] # depth-first order
  transition_list: List[Transition] # source state depth-first order, then document order
  semantics: SemanticConfiguration = SemanticConfiguration()

class Model:
  def __init__(self):
    self.event_namespace: EventNamespace = EventNamespace()
    self.inports: List[str] = []
    self.outports: List[str] = []
    self.classes: Dict[str, Statechart] = {}
    self.default_class: Optional[str] = None
