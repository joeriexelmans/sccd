from abc import *
from sccd.realtime.time import *
from sccd.controller.controller import *

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
        self.controller.run_until(self.timer.now() - self.purposefully_behind)

        # back to sleep
        now = self.timer.now()
        next_wakeup = self.controller.next_wakeup()
        if next_wakeup:
            sleep_duration = self.to_event_loop_unit(next_wakeup - now)
            if sleep_duration < 0:
                self.purposefully_behind = now - next_wakeup
                sleep_duration = 0
            else:
                self.purposefully_behind = 0
            self.scheduled = self.event_loop.schedule(sleep_duration, self._wakeup)
        else:
            self.scheduled = None

    def start(self):
        self.timer.start()
        self._wakeup()

    def now(self):
        return self.timer.now() - self.purposefully_behind

    # Uncomment if ever needed:
    # Does not mix well with interrupt().
    # def pause(self):
    #     self.timer.pause()
    #     self.event_loop.cancel()(self.scheduled)

    def interrupt(self):
        if self.scheduled:
            self.event_loop.cancel(self.scheduled)
        self.event_loop.schedule(0, self._wakeup)
