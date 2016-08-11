from sccd.runtime.infinity import INFINITY
from heapq import heappush, heappop

class EventQueue(object):
    def __init__(self):
        self.event_list = []
        self.event_time_numbers = {}
    
    def __str__(self):
        return str(self.event_list)
    
    def isEmpty(self):
        return not self.event_list
    
    def getEarliestTime(self):
        return INFINITY if self.isEmpty() else self.event_list[0][0]
    
    def add(self, event_time, event):
        self.event_time_numbers[event_time] = self.event_time_numbers.setdefault(event_time, 0) + 1
        heappush(self.event_list, (event_time, self.event_time_numbers[event_time], event))
        return id(event)
    
    def remove(self, event_id):
        self.event_list = sorted([e for e in self.event_list if id(e) != event_id])
    
    def pop(self):
        return heappop(self.event_list)[2]