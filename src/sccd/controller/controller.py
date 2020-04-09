import queue
import dataclasses
from typing import Dict, List, Optional
from sccd.controller.event_queue import *
from sccd.statechart.dynamic.event import *
from sccd.controller.object_manager import *
from sccd.util.debug import print_debug
from sccd.cd.cd import *

# The Controller class is a primitive that can be used to build backends of any kind:
# Threads, integration with existing event loop, game loop, test framework, ...
# The Controller class itself is NOT thread-safe.
class Controller:

    @dataclasses.dataclass(eq=False, frozen=True)
    class EventQueueEntry:
        event: Event
        targets: List[Instance]

    def __init__(self, cd: AbstractCD):
        self.cd = cd
        self.object_manager = ObjectManager(cd)
        self.queue: EventQueue[int, EventQueueEntry] = EventQueue()

        self.simulated_time = 0 # integer
        self.initialized = False

        self.cd.globals.assert_ready()
        # print_debug("model delta is %s" % str(self.cd.globals.delta))

        # First call to 'run_until' method initializes
        self.run_until = self._run_until_w_initialize


    def add_input(self, input: Event, time_offset: int):
            if input.name == "":
                raise Exception("Input event can't have an empty name.")
        
            # try:
            #     self.cd.globals.inports.get_id(input.port)
            # except KeyError as e:
            #     raise Exception("No such port: '%s'" % input.port) from e

            try:
                event_id = self.cd.globals.events.get_id(input.name)
            except KeyError as e:
                raise Exception("No such event: '%s'" % input.name) from e

            input.id = event_id

            # For now, add events received on input ports to all instances.
            # In the future, we can optimize this by keeping a mapping from port name to a list of instances
            # potentially responding to the event
            self.queue.add(self.simulated_time + time_offset,
                Controller.EventQueueEntry(input, self.object_manager.instances))

    # Get timestamp of next entry in event queue
    def next_wakeup(self) -> Optional[int]:
        return self.queue.earliest_timestamp()

    # Returns duration since start
    def get_simulated_duration(self) -> Duration:
        return (self.cd.globals.delta * self.simulated_time)

    def _run_until_w_initialize(self, now: Optional[int], pipe: queue.Queue):
        # first run...
        # initialize the object manager, in turn initializing our default class
        # and adding the generated events to the queue
        for i in self.object_manager.instances:
            events = i.initialize()
            self._process_big_step_output(events, pipe)
        print_debug("initialized. time is now %s" % str(self.get_simulated_duration()))

        # Next call to 'run_until' will call '_run_until'
        self.run_until = self._run_until

        # Let's try it out :)
        self.run_until(now, pipe)

    # Run until the event queue has no more due events wrt given timestamp and until all instances are stable.
    # If no timestamp is given (now = None), run until event queue is empty.
    def _run_until(self, now: Optional[int], pipe: queue.Queue):
        # Actual "event loop"
        for timestamp, entry in self.queue.due(now):
            if timestamp != self.simulated_time:
                # make time leap
                self.simulated_time = timestamp
                print_debug("\ntime is now %s" % str(self.get_simulated_duration()))
            # run all instances for whom there are events
            for instance in entry.targets:
                output = instance.big_step([entry.event])
                # print_debug("completed big step (time = %s)" % str(self.cd.globals.delta * self.simulated_time))
                self._process_big_step_output(output, pipe)

        self.simulated_time = now

    # Helper. Put big step output events in the event queue or add them to the right output listeners.
    def _process_big_step_output(self, events: List[OutputEvent], pipe: queue.Queue):
        pipe_events = []
        for e in events:
            if isinstance(e.target, InstancesTarget):
                offset = self._duration_to_time_offset(e.time_offset)
                self.queue.add(self.simulated_time + offset, Controller.EventQueueEntry(e.event, e.target.instances))
            elif isinstance(e.target, OutputPortTarget):
                assert (e.time_offset == duration(0)) # cannot combine 'after' with 'output port'
                pipe_events.append(e.event)
            else:
                raise Exception("Unexpected type:", e.target)
        if pipe_events:
            pipe.put(pipe_events, block=True, timeout=None)

    # Helper
    def _duration_to_time_offset(self, d: Duration) -> int:
        if self.cd.globals.delta == duration(0):
            return 0
        return d // self.cd.globals.delta
