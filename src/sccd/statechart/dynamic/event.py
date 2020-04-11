import termcolor
from dataclasses import *
from abc import *
from typing import *
from sccd.util.duration import *

# A raised event.
class Event:
    __slots__ = ["id", "name", "port", "params"]

    def __init__(self, id, name, port = "", params = []):
        self.id: int = id
        self.name: str = name
        self.port: str = port
        self.params: List[Any] = params

    def __eq__(self, other):
        return self.id == other.id and self.port == other.port and self.params == other.params

    def __str__(self):
        if self.port:
            s = "Event("+self.port+"."+self.name
        else:
            s = "Event("+self.name
        if self.params:
            s += str(self.params)
        s += ")"
        return termcolor.colored(s, 'yellow')

    def __repr__(self):
        return self.__str__()

# Abstract class.
class EventTarget(ABC):
    __slots__ = []

    @abstractmethod
    def __init__(self):
        pass

# A raised output event with a target and a time offset.
class OutputEvent:
    __slots__ = ["event", "target", "time_offset"]

    def __init__(self, event: Event, target: EventTarget, time_offset: int = (0)):
        self.event = event
        self.target = target
        self.time_offset = time_offset

class OutputPortTarget(EventTarget):
    __slots__ = ["outport"]

    def __init__(self, outport: str):
        self.outport = outport

class InstancesTarget(EventTarget):
    __slots__ = ["instances"]

    def __init__(self, instances):
        self.instances = instances
