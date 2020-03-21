import queue
import dataclasses
from typing import Dict, List, Optional
from sccd.controller.event_queue import *
from sccd.execution.event import *
from sccd.controller.object_manager import *
from sccd.util.debug import print_debug
from sccd.model.model import *

@dataclasses.dataclass
class InputEvent:
  name: str
  port: str
  parameters: List[Any]
  time_offset: Timestamp

# The Controller class is a primitive that can be used to build backends of any kind:
# Threads, integration with existing event loop, game loop, test framework, ...
# The Controller class itself is NOT thread-safe.
class Controller:

    @dataclasses.dataclass(eq=False, frozen=True)
    class EventQueueEntry:
        event: Event
        targets: List[Instance]

    def __init__(self, model: AbstractModel):
        self.model = model
        self.object_manager = ObjectManager(model)
        self.queue: EventQueue[EventQueueEntry] = EventQueue()

        self.simulated_time = 0 # integer
        self.initialized = False

        self.model.globals.assert_ready()
        print_debug("model delta is %s" % str(self.model.globals.delta))

    # time_offset: the offset relative to the current simulated time
    # (the timestamp given in the last call to run_until)
    def add_input(self, input: InputEvent):
            if input.name == "":
                raise Exception("Input event can't have an empty name.")
        
            if input.port not in self.model.globals.inports:
                raise Exception("No such port: '" + input.port + "'")


            e = Event(
                id=self.model.globals.get_event_id(input.name),
                name=input.name,
                port=input.port,
                parameters=input.parameters)

            # For now, add events received on input ports to all instances.
            # In the future, we can optimize this by keeping a mapping from port name to a list of instances
            # potentially responding to the event
            self.queue.add(self.simulated_time+input.time_offset,
                Controller.EventQueueEntry(e, self.object_manager.instances))

    # Get timestamp of next entry in event queue
    def next_wakeup(self) -> Optional[Timestamp]:
        return self.queue.earliest_timestamp()

    # Returns duration since start
    def get_simulated_duration(self) -> Duration:
        return (self.model.globals.delta * self.simulated_time).normalize()

    # Run until the event queue has no more due events wrt given timestamp and until all instances are stable.
    # If no timestamp is given (now = None), run until event queue is empty.
    def run_until(self, now: Optional[Timestamp], pipe: queue.Queue, interrupt: queue.Queue = queue.SimpleQueue()):

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
        def do_stabilize():
            while unstable:
                for i in reversed(range(len(unstable))):
                    instance = unstable[i]
                    stable, output = instance.big_step(self.simulated_time, [])
                    process_big_step_output(output)
                    if stable:
                        del unstable[i]
                try:
                    interrupt.get_nowait()
                    return False # interrupted
                except queue.Empty:
                    pass
            else:
                # already stable
                return True
            print_debug("all instances stabilized.")
            return True


        if not self.initialized:
            self.initialized = True

            print_debug("time is now %s" % str(self.get_simulated_duration()))
            # first run...
            # initialize the object manager, in turn initializing our default class
            # and adding the generated events to the queue
            for i in self.object_manager.instances:
                stable, events = i.initialize(self.simulated_time)
                process_big_step_output(events)
                if not stable:
                    unstable.append(i)


        # Actual "event loop"
        # TODO: What is are the right semantics for this loop?
        # Should we stabilize every object after it has made a big step?
        # Should we only stabilize when there are no more events?
        # Should we never stabilize?
        # Should this be a semantic option?
        while unstable or self.queue.is_due(now):
            # 1. Handle events
            for timestamp, entry in self.queue.due(now):
                # check if there's a time leap
                if timestamp is not self.simulated_time:
                    # before every "time leap", continue to run instances until they are stable.
                    if not do_stabilize():
                        return
                    # make time leap
                    self.simulated_time = timestamp
                    print_debug("\ntime is now %s" % str(self.get_simulated_duration()))
                # run all instances for whom there are events
                for instance in entry.targets:
                    stable, output = instance.big_step(timestamp, [entry.event])
                    # print_debug("completed big step (time = %s)" % str(self.model.globals.delta * self.simulated_time))
                    process_big_step_output(output)
                    if not stable:
                        unstable.append(instance)
            # 2. No more due events -> stabilize
            if not do_stabilize():
                return

        self.simulated_time = now
