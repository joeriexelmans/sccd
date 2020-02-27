import dataclasses
from abc import ABC, abstractmethod
from typing import List, Any
from sccd.runtime.event_queue import Timestamp

@dataclasses.dataclass(frozen=True)
class Event:
    name: str
    port: str = ""
    parameters: List[Any] = dataclasses.field(default_factory=list)

# Abstract class.
class EventTarget(ABC):
    @abstractmethod
    def __init__(self):
        pass

# An event with a target and a time offset.
class OutputEvent:
    def __init__(self, event: Event, target: EventTarget, time_offset=0):
        self.event = event
        self.target = target
        self.time_offset = time_offset

# Interface for all instances and also the Object Manager
class Instance(ABC):
    @abstractmethod
    def big_step(self, timestamp: Timestamp, input_events: List[Event]) -> List[OutputEvent]:
        pass

    @abstractmethod
    def is_stable(self) -> bool:
        pass


class OutputPortTarget(EventTarget):
    def __init__(self, outport: str):
        self.outport = outport

class InstancesTarget(EventTarget):
    def __init__(self, instances: List[Instance]):
        self.instances = instances
