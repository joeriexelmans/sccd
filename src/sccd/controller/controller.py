import queue
import dataclasses
from typing import Dict, List, Optional
from sccd.controller.event_queue import *
from sccd.statechart.dynamic.event import *
from sccd.controller.object_manager import *
from sccd.util.debug import print_debug
from sccd.cd.cd import *

def _dummy_output_callback(output_event):
    pass

# The Controller class is a primitive that can be used to build backends of any kind:
# Threads, integration with existing event loop, game loop, test framework, ...
# The Controller class itself is NOT thread-safe.
class Controller:
    __slots__ = ["cd", "object_manager", "queue", "simulated_time", "run_until"]

    @dataclasses.dataclass(eq=False, frozen=True)
    class EventQueueEntry:
        __slots__ = ["event", "targets"]
        event: InternalEvent
        targets: List[Instance]

        def __repr__(self):
            return "QueueEntry("+str(self.event)+")"


    def __init__(self, cd: AbstractCD, output_callback: Callable[[OutputEvent],None] = _dummy_output_callback):
        cd.globals.assert_ready()
        self.cd = cd

        self.simulated_time = 0 # integer

        def schedule_after(after, event, instances):
            entry = Controller.EventQueueEntry(event, instances)
            self.queue.add(self.simulated_time + after, entry)
            return entry

        def cancel_after(entry):
            self.queue.remove(entry)

        self.object_manager = ObjectManager(cd, output_callback, schedule_after, cancel_after)

        self.queue: EventQueue[int, EventQueueEntry] = EventQueue()

        if DEBUG:
            self.cd.print()
            print("Model delta is %s" % str(self.cd.globals.delta))

        # First call to 'run_until' method initializes
        self.run_until = self._run_until_w_initialize


    def get_model_delta(self) -> Duration:
        return self.cd.globals.delta

    def schedule(self, timestamp: int, event: InternalEvent, instances: List[Instance]):
        self.queue.add(timestamp, Controller.EventQueueEntry(event, instances))

    def inport_to_instances(self, port: str) -> List[Instance]:
        try:
            self.cd.globals.inports.get_id(port)
        except KeyError as e:
            raise Exception("No such port: '%s'" % port) from e

        # For now, we just broadcast all input events.
        # We don't even check if the event is allowed on the input port.
        # TODO: multicast event only to instances that subscribe to this port.
        return self.object_manager.instances

    def add_input(self, timestamp: int, port: str, event_name: str, params = []):
        try:
            event_id = self.cd.globals.events.get_id(event_name)
        except KeyError as e:
            raise Exception("No such event: '%s'" % event_name) from e

        instances = self.inport_to_instances(port)
        event = InternalEvent(event_id, event_name, params)

        self.schedule(timestamp, event, instances)

    # Get timestamp of next entry in event queue
    def next_wakeup(self) -> Optional[int]:
        return self.queue.earliest_timestamp()

    def _run_until_w_initialize(self, now: Optional[int]):
        # first run...
        # initialize the object manager, in turn initializing our default class
        # and adding the generated events to the queue
        for i in self.object_manager.instances:
            i.initialize()
        if DEBUG:
            print("initialized.")

        # Next call to 'run_until' will call '_run_until'
        self.run_until = self._run_until

        # Let's try it out :)
        self.run_until(now)

    # Run until the event queue has no more due events wrt given timestamp and until all instances are stable.
    # If no timestamp is given (now = None), run until event queue is empty.
    def _run_until(self, now: Optional[int]):
        # Actual "event loop"
        for timestamp, entry in self.queue.due(now):
            if timestamp != self.simulated_time:
                # make time leap
                self.simulated_time = timestamp
                if DEBUG:
                    print("\ntime is now %s" % str(self.cd.globals.delta * self.simulated_time))
            # print("popped", entry)
            # print("remaining", self.queue)
            # run all instances for whom there are events
            for instance in entry.targets:
                instance.big_step([entry.event])
                # print_debug("completed big step (time = %s)" % str(self.cd.globals.delta * self.simulated_time))
