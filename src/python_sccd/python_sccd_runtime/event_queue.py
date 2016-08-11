from sccd.runtime.infinity import INFINITY
from heapq import heappush, heappop

class EventQueue(object):
    def __init__(self):
        self.event_list = []
        self.event_time_numbers = {}
        self.removed = set()
    
    def __str__(self):
        return str(self.event_list)
    
    def isEmpty(self):
        return not self.event_list
    
    def getEarliestTime(self):
        return INFINITY if self.isEmpty() else self.event_list[0][0]
    
    def add(self, event_time, event):
        self.event_time_numbers[event_time] = self.event_time_numbers.setdefault(event_time, 0) + 1
        heappush(self.event_list, (event_time, self.event_time_numbers[event_time], event))
        return event
    
    def remove(self, event):
        self.removed.add(event)
    
    def pop(self):
        while 1:
            item = heappop(self.event_list)
            event_time = item[0]
            self.event_time_numbers[event_time] -= 1
            if not self.event_time_numbers[event_time]:
                del self.event_time_numbers[event_time]
            if item not in self.removed:
                return item[2]
            else:
                self.removed.remove(item)