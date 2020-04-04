from abc import *
from typing import *
from sccd.execution.event import *
from sccd.execution.timestamp import *

# Interface for all instances and also the Object Manager
class Instance(ABC):
    @abstractmethod
    def initialize(self, timestamp: Timestamp) -> List[OutputEvent]:
        pass

    @abstractmethod
    def big_step(self, timestamp: Timestamp, input_events: List[Event]) -> List[OutputEvent]:
        pass
