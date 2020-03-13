from typing import *
from dataclasses import *
from sccd.syntax.expression import *
from sccd.syntax.statement import *

@dataclass
class Action:
    pass

@dataclass
class RaiseEvent(Action):
    name: str
    parameters: List[Expression]

    # just a simple string representation for rendering a transition label
    def render(self) -> str:
        return '^'+self.name

@dataclass
class RaiseInternalEvent(RaiseEvent):
    event_id: int

@dataclass
class RaiseOutputEvent(RaiseEvent):
    outport: str
    time_offset: int

    def render(self) -> str:
        return '^'+self.outport + '.' + self.name

@dataclass
class Code(Action):
    block: Block
