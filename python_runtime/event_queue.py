from infinity import INFINITY

class EventQueue(object):
    def __init__(self):
        self.event_list = []
    
    def __str__(self):
        return str(self.event_list)
    
    def isEmpty(self):
        return not self.event_list
    
    def getEarliestTime(self):
        return INFINITY if self.isEmpty() else self.event_list[0][0]
    
    def add(self, event):
        self.event_list.append(event)
        self.event_list.sort()
        return id(event)
    
    def remove(self, event_id):
        self.event_list = sorted([e for e in self.event_list if id(e) != event_id])
    
    def pop(self):
        return self.event_list.pop(0)[1]