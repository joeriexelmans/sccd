from abc import *
from sccd.realtime.time import *
from sccd.controller.controller import *
import queue

ScheduledID = Any

# The interface for declaring 3rd party event loop implementations
@dataclass
class EventLoopImplementation(ABC):
    @abstractmethod
    def time_unit(self) -> Duration:
        pass

    @abstractmethod
    def schedule(self, timeout: int, callback: Callable[[],None]) -> ScheduledID:
        pass

    @abstractmethod
    def cancel(self, id: ScheduledID):
        pass

# Event loop "platform".
# This class is NOT thread-safe.
class EventLoop:
    def __init__(self, controller: Controller, event_loop: EventLoopImplementation, time_impl: TimeImplementation = DefaultTimeImplementation):
        delta = controller.cd.get_delta()
        self.timer = Timer(time_impl, unit=delta) # will give us timestamps in model unit
        self.controller = controller
        self.event_loop = event_loop

        # got to convert from model unit to eventloop native unit for scheduling
        self.to_event_loop_unit = lambda x: int(get_conversion_f(delta, event_loop.time_unit())(x))

        # ID of currently scheduled task.
        # The actual type of this attribute depends on the event loop implementation.
        self.scheduled = None

        # Keeps the model responsive if we cannot keep up with wallclock time.
        self.purposefully_behind = 0

    def _wakeup(self):
        self.controller.run_until(self.timer.now() + self.purposefully_behind)

        # back to sleep
        next_wakeup = self.controller.next_wakeup()

        if next_wakeup is not None:
            sleep_duration = next_wakeup - self.timer.now()
            if sleep_duration < 0:
                self.purposefully_behind = sleep_duration
                sleep_duration = 0
            else:
                self.purposefully_behind = 0

            self.scheduled = self.event_loop.schedule(self.to_event_loop_unit(sleep_duration), self._wakeup)
        else:
            self.scheduled = None

    def start(self):
        self.timer.start()
        self._wakeup()

    def now(self):
        return self.timer.now() + self.purposefully_behind

    # Add input event with timestamp 'now'
    def add_input_now(self, port, event_name, params=[]):
        self.controller.add_input(
            timestamp=self.now(), port=port, event_name=event_name, params=params)
        if self.scheduled:
            self.event_loop.cancel(self.scheduled)
        self.event_loop.schedule(0, self._wakeup)


# Extension to the EventLoop class with a thread-safe method for adding input events.
# Allows other threads to add input to the Controller, which is useful when doing blocking IO.
# It is probably cleaner to do async IO and use the regular EventLoop class instead.
# Input events added in a thread-safe manner are added to a separate (thread-safe) queue. A bit hackish, this queue is regularly checked (polled) for new events from the 3rd party (e.g. Tk) event loop.
# Perhaps a better alternative to polling is Yentl's tk.event_generate solution.
class ThreadSafeEventLoop(EventLoop):
    def __init__(self, controller: Controller, event_loop: EventLoopImplementation, time_impl: TimeImplementation = DefaultTimeImplementation):
        super().__init__(controller, event_loop, time_impl)

        # thread-safe queue
        self.queue = queue.Queue()

        # check regularly if queue contains new events
        self.poll_interval = duration(100, Millisecond) // event_loop.time_unit()

    # override
    def _wakeup(self):
        while True:
            try:
                timestamp, port, event_name, params = self.queue.get_nowait()
            except queue.Empty:
                break
            self.controller.add_input(timestamp, port, event_name, params)

        self.controller.run_until(self.timer.now() + self.purposefully_behind)

        next_wakeup = self.controller.next_wakeup()
        if next_wakeup is not None:
            sleep_duration = next_wakeup - self.timer.now()
            if sleep_duration < 0:
                self.purposefully_behind = sleep_duration
                sleep_duration = 0
            else:
                self.purposefully_behind = 0
            self.scheduled = self.event_loop.schedule(min(self.to_event_loop_unit(sleep_duration), self.poll_interval), self._wakeup)
        else:
            self.scheduled = self.event_loop.schedule(self.poll_interval, self._wakeup)

    # Safe to call this method from any thread
    def add_input_now_threadsafe(self, port, event_name, params=[]):
        self.queue.put((self.now(), port, event_name, params))
