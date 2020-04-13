from abc import *
from sccd.realtime.time import *
from sccd.controller.controller import *

ScheduledID = Any

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
        delta = controller.get_model_delta()
        self.timer = Timer(time_impl, unit=delta) # will give us timestamps in model unit
        self.controller = controller
        self.event_loop = event_loop

        # got to convert from model unit to eventloop native unit for scheduling
        self.to_event_loop_unit = lambda x: int(get_conversion_f(delta, event_loop.time_unit())(x))

        self.scheduled = None

    def _wakeup(self):
        self.controller.run_until(self.timer.now())

        # back to sleep
        now = self.timer.now()
        next_wakeup = self.controller.next_wakeup()
        if next_wakeup:
            # (next_wakeup - now) is negative, we are running behind
            # not much we can do about it though
            sleep_duration = max(0, self.to_event_loop_unit(next_wakeup - now))
            self.scheduled = self.event_loop.schedule(sleep_duration, self._wakeup)
        else:
            self.scheduled = None

    def start(self):
        self.timer.start()
        self._wakeup()

    def now(self):
        return self.timer.now()

    # Uncomment if ever needed:
    # Does not mix well with interrupt().
    # def pause(self):
    #     self.timer.pause()
    #     self.event_loop.cancel()(self.scheduled)

    def interrupt(self):
        if self.scheduled:
            self.event_loop.cancel(self.scheduled)
        self._wakeup()
