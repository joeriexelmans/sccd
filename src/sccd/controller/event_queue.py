from heapq import heappush, heappop, heapify
from abc import ABC
from typing import List, Set, Tuple, Deque, Any, TypeVar, Generic, Generator, Optional
from collections import deque
from  sccd.util import timer

Timestamp = TypeVar('Timestamp')
Item = TypeVar('Item')

class EventQueue(Generic[Timestamp, Item]):
    __slots__ = ["queue", "counters", "removed"]

    def __init__(self):
        self.queue: List[Tuple[Timestamp, int, Item]] = []
        self.counters = {} # mapping from timestamp to number of items at timestamp
        self.removed: Set[Item] = set()
    
    def __str__(self):
        return str([entry for entry in self.queue if entry[2] not in self.removed])
    
    def is_empty(self) -> bool:
        return not [item for item in self.queue if not item[2] in self.removed]
    
    def earliest_timestamp(self) -> Optional[Timestamp]:
        while self.queue and (self.queue[0] in self.removed):
            item = heappop(self.queue)
            self.removed.remove(item[2])
        try:
            return self.queue[0][0]
        except IndexError:
            return None
    
    def add(self, timestamp: Timestamp, item: Item):
        with timer.Context("event_queue"):
            self.counters[timestamp] = self.counters.setdefault(timestamp, 0) + 1
            def_event = (timestamp, self.counters[timestamp], item)
            heappush(self.queue, def_event)
    
    def remove(self, item: Item):
        with timer.Context("event_queue"):
            self.removed.add(item)
            if len(self.removed) > 100:
                self.queue = [x for x in self.queue if x not in self.removed]
                heapify(self.queue)
                self.removed = set()

    # Raises exception if called on empty queue
    def pop(self) -> Tuple[Timestamp, Item]:
        with timer.Context("event_queue"):
            while 1:
                item = heappop(self.queue)
                timestamp = item[0]
                self.counters[timestamp] -= 1
                if not self.counters[timestamp]:
                    del self.counters[timestamp]
                if item[2] not in self.removed:
                    return (timestamp, item[2])

    def is_due(self, timestamp: Optional[Timestamp]) -> bool:
        return len(self.queue) and (timestamp == None or self.queue[0][0] <= timestamp)

    # Safe to call on empty queue
    # Safe to call other methods on the queue while the returned generator exists
    def due(self, timestamp: Optional[Timestamp]) -> Generator[Tuple[Timestamp, Item], None, None]:
        while self.is_due(timestamp):
            yield self.pop()
