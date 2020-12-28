import termcolor
from dataclasses import *
from abc import *
from typing import *
from sccd.util.duration import *

# An event that can cause transitions to happen.
# Input events are internal events too.
@dataclass
class InternalEvent:
    __slots__ = ["name", "params"]

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
    __slots__ = ["name", "params"]

    # port: str
    name: str
    params: List[Any]

    # Compare by value
    def __eq__(self, other):
        # return self.port == other.port and self.name == other.name and self.params == other.params
        return self.name == other.name and self.params == other.params

    def __str__(self):
        s = "OutputEvent("+self.name
        if self.params:
            s += str(self.params)
        s += ")"
        return termcolor.colored(s, 'yellow')

    __repr__ = __str__
