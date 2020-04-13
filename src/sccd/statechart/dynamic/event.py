import termcolor
from dataclasses import *
from abc import *
from typing import *
from sccd.util.duration import *

# An event that can cause transitions to happen.
# Input events are internal events too.
@dataclass
class InternalEvent:
    __slots__ = ["id", "name", "params"]

    id: int
    name: str # solely used for pretty printing
    params: List[Any]

    def __str__(self):
        s = "Event("+self.name
        if self.params:
            s += str(self.params)
        s += ")"
        return termcolor.colored(s, 'yellow')

    __repr__ = __str__



@dataclass
class OutputEvent:
    __slots__ = ["port", "name", "params"]

    port: str
    name: str
    params: List[Any]

    # Compare by value
    def __eq__(self, other):
        return self.port == other.port and self.name == other.name and self.params == other.params

    def __str__(self):
        s = "OutputEvent("+self.port+"."+self.name
        if self.params:
            s += str(self.params)
        s += ")"
        return termcolor.colored(s, 'yellow')

    __repr__ = __str__

# # A raised event.
# class Event:
#     __slots__ = ["id", "name", "port", "params"]

#     def __init__(self, id, name, port = "", params = []):
#         self.id: int = id
#         self.name: str = name
#         self.port: str = port
#         self.params: List[Any] = params

#     def __eq__(self, other):
#         return self.id == other.id and self.port == other.port and self.params == other.params

#     def __str__(self):
#         if self.port:
#             s = "Event("+self.port+"."+self.name
#         else:
#             s = "Event("+self.name
#         if self.params:
#             s += str(self.params)
#         s += ")"
#         return termcolor.colored(s, 'yellow')

#     def __repr__(self):
#         return self.__str__()

# # Abstract class.
# class EventTarget(ABC):
#     __slots__ = []

#     @abstractmethod
#     def __init__(self):
#         pass

# # A raised output event with a target and a time offset.
# class OutputEvent:
#     __slots__ = ["event", "target", "time_offset"]

#     def __init__(self, event: Event, target: EventTarget, time_offset: int = (0)):
#         self.event = event
#         self.target = target
#         self.time_offset = time_offset

# class OutputPortTarget(EventTarget):
#     __slots__ = ["outport"]

#     def __init__(self, outport: str):
#         self.outport = outport

# class InstancesTarget(EventTarget):
#     __slots__ = ["instances"]

#     def __init__(self, instances):
#         self.instances = instances
