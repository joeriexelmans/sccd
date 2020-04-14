from heapq import heappush, heappop, heapify
from abc import ABC
from typing import List, Set, Tuple, Deque, Any, TypeVar, Generic, Generator, Optional
from collections import deque
from  sccd.util import timer

Timestamp = TypeVar('Timestamp')
Item = TypeVar('Item')

class EventQueue(Generic[Timestamp, Item]):
    __slots__ = ["queue", "counters", "removed"]

    # We don't define our own event queue item class here
    # with __lt__ because tuples are faster to compare.
    # Tuples are however immutable, so we "wrap" the 'removed'
    # flag in an object:
    class RemovedWrapper:
        __slots__ = ["removed"]
        def __init__(self):
            self.removed = False

    def __init__(self):
        self.queue: List[Tuple[Timestamp, int, RemovedWrapper, Item]] = []
        self.counters = {} # mapping from timestamp to number of items at timestamp

    def __str__(self):
        return str(sorted([tup for tup in self.queue if not tup[2].removed]))

    def earliest_timestamp(self) -> Optional[Timestamp]:
        with timer.Context("event_queue"):
            while self.queue and self.queue[0][2].removed:
                heappop(self.queue)
            try:
                return self.queue[0][0]
            except IndexError:
                return None

    def add(self, timestamp: Timestamp, item: Item):
        # print("add", item)
        with timer.Context("event_queue"):
            n = self.counters[timestamp] = self.counters.setdefault(timestamp, 0) + 1
            def_event = (timestamp, n, EventQueue.RemovedWrapper(), item)
            heappush(self.queue, def_event)
            return def_event

    def remove(self, item: Tuple[Timestamp, int, RemovedWrapper, Item]):
        # print("remove", item)
        with timer.Context("event_queue"):
            item[2].removed = True

    # Raises exception if called on empty queue
    def pop(self) -> Tuple[Timestamp, Item]:
        with timer.Context("event_queue"):
            while 1:
                timestamp, n, removed, item = heappop(self.queue)
                if self.counters[timestamp] == n:
                    del self.counters[timestamp]
                if not removed.removed:
                    return (timestamp, item)

    def is_due(self, timestamp: Optional[Timestamp]) -> bool:
        earliest = self.earliest_timestamp()
        # print("is_due", earliest, timestamp, earliest is not None and (timestamp is None or earliest <= timestamp))

        return earliest is not None and (timestamp is None or earliest <= timestamp)

    # Safe to call on empty queue
    # Safe to call other methods on the queue while the returned generator exists
    def due(self, timestamp: Optional[Timestamp]) -> Generator[Tuple[Timestamp, Item], None, None]:
        while self.is_due(timestamp):
            yield self.pop()
