from sccd.statechart.dynamic.event import InternalEvent
from sccd.statechart.parser.xml import *
from sccd.statechart.static.globals import *
from sccd.cd.static.cd import *


@dataclass
class TestInputBag:
  events: List[InternalEvent]
  timestamp: Expression

@dataclass
class TestVariant:
  name: str
  cd: AbstractCD
  input: List[TestInputBag]
  output: List[List[OutputEvent]]
