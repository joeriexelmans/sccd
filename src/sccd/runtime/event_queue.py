from sccd.runtime.infinity import INFINITY
from heapq import heappush, heappop, heapify
from abc import ABC
from typing import List, Set, Tuple, Deque, Any, TypeVar, Generic, Generator
from collections import deque

Timestamp = int

Item = TypeVar('Item')

class EventQueue(Generic[Item]):
    def __init__(self):
        self.queue: List[Tuple[Timestamp, int, Item]] = []
        self.counters = {} # mapping from timestamp to number of items at timestamp
        self.removed: Set[Item] = set()
    
    def __str__(self):
        return str([entry for entry in self.queue if entry[2] not in self.removed])
    
    def is_empty(self) -> bool:
        return not [item for item in self.queue if not item[2] in self.removed]
    
    def earliest_timestamp(self) -> Timestamp:
        while self.queue and (self.queue[0] in self.removed):
            item = heappop(self.queue)
            self.removed.remove(item)
        try:
            return self.queue[0][0]
        except IndexError:
            return INFINITY
    
    def add(self, timestamp: Timestamp, item: Item):
        self.counters[timestamp] = self.counters.setdefault(timestamp, 0) + 1
        def_event = (timestamp, self.counters[timestamp], item)
        heappush(self.queue, def_event)
        return def_event
    
    def remove(self, item: Item):
        self.removed.add(item)
        if len(self.removed) > 100:
            self.queue = [x for x in self.queue if x not in self.removed]
            self.removed = set()
    
    # Raises exception if called on empty queue
    def pop(self) -> Tuple[Timestamp, Item]:
        while 1:
            item = heappop(self.queue)
            timestamp = item[0]
            self.counters[timestamp] -= 1
            if not self.counters[timestamp]:
                del self.counters[timestamp]
            if item[2] not in self.removed:
                return (timestamp, item[2])

    # Safe to call on empty queue
    # Safe to call other methods on the queue while the returned generator exists
    def due(self, timestamp: Timestamp) -> Generator[Tuple[Timestamp, Item], None, None]:
        while len(self.queue) and self.queue[0][0] <= timestamp:
            yield self.pop()

# Alternative implementation: A heapq with unique entries for each timestamp, and a deque with items for each timestamp.
class EventQueueDeque(Generic[Item]):
    Entry = Tuple[Timestamp, Deque[Item]]

    def __init__(self):
        self.queue: List[Entry] = []
        self.entries: Dict[Timestamp, Deque[Item]] = {}

        # performance optimization:
        # removed items are not immediately removed from the queue,
        # instead they are added to the following set:
        self.removed: Set[Item] = set()

    def is_empty(self) -> bool:
        for x in self.queue:
            for y in x[1]:
                if y not in self.removed:
                    return False
        return True

    def earliest_timestamp(self) -> Timestamp:
        try:
            earliest, _ = self.queue[0]
            return earliest
        except IndexError:
            return INFINITY

    def add(self, timestamp: Timestamp, item: Item):
        try:
            # entry at timestamp already exists:
            self.entries[timestamp].append(item)
        except KeyError:
            # need to create entry
            d = deque([item])
            self.entries[timestamp] = d
            heappush(self.queue, (timestamp, d))

    def remove(self, item: Item):
        self.removed.add(item)
        if len(self.removed) > 5:
            # to remove some elements safely from list while iterating over it and without copying the list,
            # we iterate backwards:
            for i in range(len(self.queue)-1, -1, -1):
                queue_entry = self.queue[i]
                timestamp, old_deque = queue_entry
                new_deque = deque([])
                for item in old_deque:
                    if item not in self.removed:
                        new_deque.append(item)
                if not new_deque:
                    del self.entries[timestamp]
                    del self.queue[i]
                else:
                    self.queue[i] = (timestamp, new_deque)
            # not sure if the heap invariant maintained here, though
            # if not, uncomment:
            # heapify(self.queue)
            self.removed = set()

    # Raises exception if called on empty queue
    def pop(self) -> Tuple[Timestamp, Item]:
        while True:
            timestamp, d = self.queue[0]
            while True:
                item = d.popleft()
                if not d: # deque empty - get rid of entry
                    del self.entries[timestamp]
                    heappop(self.queue)
                if item not in self.removed:
                    return (timestamp, item)
                else:
                    self.removed.remove(item)

    # Safe to call on empty queue
    # Safe to call other methods on the queue while the returned generator exists
    def due(self, timestamp: Timestamp) -> Generator[Tuple[Timestamp, Item], None, None]:
        while len(self.queue) and self.queue[0][0] <= timestamp:
            yield self.pop()
