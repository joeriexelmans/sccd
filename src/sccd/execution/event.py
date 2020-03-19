import termcolor
from dataclasses import *
from abc import *
from typing import *

# A raised event.
@dataclass(frozen=True)
class Event:
    id: int
    name: str
    port: str = ""
    parameters: List[Any] = field(default_factory=list)

    def __str__(self):
        if self.port:
            s = "Event("+self.port+"."+self.name
        else:
            s = "Event("+self.name
        if self.parameters:
            s += str(self.parameters)
        s += ")"
        return termcolor.colored(s, 'yellow')

    def __repr__(self):
        return self.__str__()

# Abstract class.
class EventTarget(ABC):
    @abstractmethod
    def __init__(self):
        pass

# A raised output event with a target and a time offset.
class OutputEvent:
    def __init__(self, event: Event, target: EventTarget, time_offset = 0):
        self.event = event
        self.target = target
        self.time_offset = time_offset

class OutputPortTarget(EventTarget):
    def __init__(self, outport: str):
        self.outport = outport

class InstancesTarget(EventTarget):
    def __init__(self, instances):
        self.instances = instances
