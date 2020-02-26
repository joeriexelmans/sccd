from abc import ABC, abstractmethod
from typing import List
from sccd.runtime.event_queue import Timestamp

# Data class.
class Event:
    def __init__(self, name, port = "", parameters = []):
        self._name = name
        self._port = port
        self._parameters = parameters

    @property
    def name(self):
        return self._name

    @property
    def port(self):
        return self._port

    @property
    def parameters(self):
        return self._parameters
    
    def __repr__(self):
        s = "Event (name: " + str(self._name) + "; port: " + str(self._port)
        if self._parameters:
            s += "; parameters: " + str(self._parameters)
        s += ")"
        return s

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

