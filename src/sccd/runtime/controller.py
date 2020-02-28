import queue
import dataclasses
from typing import Dict, List, Optional
from sccd.runtime.event_queue import EventQueue, EventQueueDeque, Timestamp
from sccd.runtime.event import *
from sccd.runtime.object_manager import ObjectManager
from sccd.runtime.infinity import INFINITY
from sccd.runtime.debug import print_debug

# The Controller class is a primitive that can be used to build backends of any kind:
# Threads, integration with existing event loop, game loop, test framework, ...
# The Controller class itself is NOT thread-safe.
class Controller:

    @dataclasses.dataclass(eq=False, frozen=True)
    class EventQueueEntry:
        event: Event
        targets: List[Instance]

    def __init__(self, model):
        self.model = model
        self.object_manager = ObjectManager(model)
        self.queue: EventQueue[EventQueueEntry] = EventQueue()

        self.simulated_time = 0 # integer
        self.initialized = False

    # time_offset: the offset relative to the current simulated time
    # (the timestamp given in the last call to run_until)
    def add_input(self, event: Event, time_offset = 0):
            if event.name == "":
                raise Exception("Input event can't have an empty name.")
        
            if event.port not in self.model.inports:
                raise Exception("No such port: '" + event.port + "'")

            # For now, add events received on input ports to all instances.
            # In the future, we can optimize this by keeping a mapping from port name to a list of instances
            # potentially responding to the event
            self.queue.add(self.simulated_time+time_offset, Controller.EventQueueEntry(event, self.object_manager.instances))

    # The following 2 methods are the basis of any kind of event loop,
    # regardless of the platform ()

    # Get timestamp of next entry in event queue
    def next_wakeup(self) -> Optional[Timestamp]:
        return self.queue.earliest_timestamp()

    # Run until given timestamp.
    # Simulation continues until there are no more due events wrt timestamp and until all instances are stable.
    # Output generated while running is written to 'pipe' so it can be heard by another thread.
    def run_until(self, now: Timestamp, pipe: queue.Queue):

        unstable: List[Instance] = []

        # Helper. Put big step output events in the event queue or add them to the right output listeners.
        def process_big_step_output(events: List[OutputEvent]):
            pipe_events = []
            for e in events:
                if isinstance(e.target, InstancesTarget):
                    self.queue.add(self.simulated_time+e.time_offset, Controller.EventQueueEntry(e.event, e.target.instances))
                elif isinstance(e.target, OutputPortTarget):
                    assert (e.time_offset == 0) # cannot combine 'after' with 'output port'
                    pipe_events.append(e.event)
                else:
                    raise Exception("Unexpected type:", e.target)
            if pipe_events:
                pipe.put(pipe_events, block=True, timeout=None)

        # Helper. Let all unstable instances execute big steps until they are stable
        def run_unstable():
            had_unstable = False
            while unstable:
                had_unstable = True
                for i in reversed(range(len(unstable))):
                    instance = unstable[i]
                    stable, output = instance.big_step(self.simulated_time, [])
                    process_big_step_output(output)
                    if stable:
                        del unstable[i]
            if had_unstable:
                print_debug("all instances stabilized.")
                pass

        if now < self.simulated_time:
            raise Exception("Simulated time can only increase!")

        if not self.initialized:
            self.initialized = True
            # first run...
            # initialize the object manager, in turn initializing our default class
            # and add the generated events to the queue
            for i in self.object_manager.instances:
                stable, events = i.initialize(self.simulated_time)
                process_big_step_output(events)
                if not stable:
                    unstable.append(i)

        # Actual "event loop"
        for timestamp, entry in self.queue.due(now):
            # check if there's a time leap
            if timestamp is not self.simulated_time:
                # before every "time leap", continue to run instances until they are stable.
                run_unstable()
                # make time leap
                self.simulated_time = timestamp
            # run all instances for whom there are events
            for instance in entry.targets:
                stable, output = instance.big_step(timestamp, [entry.event])
                process_big_step_output(output)
                if not stable:
                    unstable.append(instance)

        # continue to run instances until all are stable
        run_unstable()

        self.simulated_time = now
