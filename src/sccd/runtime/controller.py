import threading
from typing import Dict, List
from sccd.runtime.event_queue import EventQueue, Timestamp
from sccd.runtime.event import *
from sccd.runtime.object_manager import ObjectManager
from sccd.runtime.infinity import INFINITY

# try:
from queue import Queue, Empty
# except ImportError:
#     from Queue import Queue, Empty

# try:
# except ImportError:
# from infinity import INFINITY

class OutputListener:
    def __init__(self):
        self.queue = Queue() # queue of lists of event objects
        self.done = False

    """ Called at the end of a big step with a list of events.

        Parameters
        ----------
        events: list of Event objects """
    def signal_output(self, events):
        assert not self.done
        self.queue.put_nowait(("output", events))

    def signal_exception(self, exception):
        assert not self.done
        self.queue.put_nowait(("exception", exception))

    def signal_done(self):
        assert not self.done
        self.done = True
        self.queue.put_nowait(("done", None))

    """ Fetch next element without blocking.
        If no element is available, None is returned. """
    def fetch_nonblocking(self):
        try:
            return self.queue.get_nowait()
        except Empty:
            return None

    """ Fetch next element from listener, blocking until an element is available.
        If the given timeout is exceeded, None is returned.

        Parameters
        ----------
        timeout: Max time to block (in seconds). None if allowed to block forever. """
    def fetch_blocking(self, timeout=None):
        try:
            return self.queue.get(True, timeout);
        except Empty:
            return None

# Data class
class InputPortEntry(object):
    def __init__(self, virtual_name, instance):
        self.virtual_name = virtual_name
        self.instance = instance

# Data class
class OutputPortEntry(object):
    def __init__(self, port_name, virtual_name, instance):
        self.port_name = port_name
        self.virtual_name = virtual_name
        self.instance = instance


class Controller:
    # Data class
    class EventQueueEntry:
        def __init__(self, event: Event, targets: List[Instance]):
            self.event = event
            self.targets = targets

        def __str__(self):
            return "(event:"+str(self.event)+",targets:"+str(self.targets)+")"

        def __repr__(self):
            return self.__str__()

    def __init__(self, model):
        self.model = model
        self.object_manager = ObjectManager(model)
        self.queue: EventQueue[EventQueueEntry] = EventQueue()

        # keep track of input ports
        self.output_listeners: Dict[str, List[OutputListener]] = {} # dictionary from port name to list of OutputListener objects

        self.simulated_time = 0 # integer
        self.initialized = False

    def addInput(self, event: Event, time_offset = 0):
            if event.name == "":
                raise Exception("Input event can't have an empty name.")
        
            if event.port not in self.model.inports:
                raise Exception("No such port: '" + event.port + "'")

            # For now, add events received on input ports to all instances.
            # In the future, we can optimize this by keeping a mapping from port name to a list of instances
            # potentially responding to the event
            self.queue.add(self.simulated_time+time_offset, Controller.EventQueueEntry(event, self.object_manager.instances))

    def createOutputListener(self, ports):
        listener = OutputListener()
        self.addOutputListener(ports, listener)
        return listener

    def addOutputListener(self, ports, listener):
        if len(ports) == 0:
            # add to all the ports
            if self.model.outports:
                self.addOutputListener(self.model.outports, listener)
        else:
            for port in ports:
                self.output_listeners.setdefault(port, []).append(listener)

    # The following 2 methods are the basis of any kind of event loop,
    # regardless of the platform (Threads, integration with existing event loop, game loop, test framework, ...)

    # Get timestamp of next entry in event queue
    def next_wakeup(self) -> Timestamp:
        return self.queue.earliest_timestamp()

    # Run until given timestamp.
    # Simulation continues until there are no more due events wrt timestamp and until all instances are stable.
    def run_until(self, now: Timestamp):

        unstable = []

        def process_big_step_output(events: List[OutputEvent]):
            listener_events = {}
            for e in events:
                if isinstance(e.target, InstancesTarget):
                    self.queue.add(self.simulated_time+e.time_offset, Controller.EventQueueEntry(e.event, e.target.instances))
                elif isinstance(e.target, OutputPortTarget):
                    assert (e.time_offset == 0) # cannot combine 'after' with 'output port'
                    for listener in self.output_listeners[e.target.outport]:
                        listener_events.setdefault(listener, []).append(e.event)
                else:
                    raise Exception("Unexpected type:", e.target)
            for listener, events in listener_events.items():
                listener.signal_output(events)

        def run_unstable():
            had_unstable = False
            while unstable:
                had_unstable = True
                for i in reversed(range(len(unstable))):
                    instance = unstable[i]
                    output = instance.big_step(self.simulated_time, [])
                    process_big_step_output(output)
                    if instance.is_stable():
                        del unstable[i]
            if had_unstable:
                print("all stabilized.")

        if now < self.simulated_time:
            raise Exception("Simulated time can only increase!")

        if not self.initialized:
            self.initialized = True
            # first run...
            # initialize the object manager, in turn initializing our default class
            # and add the generated events to the queue
            for i in self.object_manager.instances:
                events = i.initialize(self.simulated_time)
                process_big_step_output(events)
                if not i.is_stable():
                    unstable.append(i)

        run_unstable()

        for timestamp, entry in self.queue.due(now):
            # run instances
            if timestamp is not self.simulated_time:
                # before every "time leap" (and also when run_until is called for the first time ever)
                # continue to run instances until they are stable.
                run_unstable()
                # make time leap
                self.simulated_time = timestamp
            for instance in entry.targets:
                output = instance.big_step(timestamp, [entry.event])
                process_big_step_output(output)
                if not instance.is_stable():
                    unstable.append(instance)

        # continue to run instances until all are stable
        run_unstable()

        self.simulated_time = now
