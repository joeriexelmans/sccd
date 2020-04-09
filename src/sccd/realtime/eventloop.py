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
    def schedule(self) -> Callable[[int, Callable[[],None]], ScheduledID]:
        pass

    @abstractmethod
    def cancel(self) -> Callable[[ScheduledID], None]:
        pass


class EventLoop:
    def __init__(self, cd: AbstractCD, event_loop: EventLoopImplementation, output_callback: Callable[[List[Event]],None], time_impl: TimeImplementation = DefaultTimeImplementation):
        self.timer = Timer(time_impl, unit=cd.globals.delta) # will give us timestamps in model unit
        self.controller = Controller(cd)
        self.event_loop = event_loop
        self.output_callback = output_callback

        self.event_loop_convert = lambda x: int(get_conversion_f(
            cd.globals.delta, event_loop.time_unit())(x)) # got to convert from model unit to eventloop native unit for scheduling

        self.scheduled = None
        self.queue = queue.Queue()

    def _wakeup(self):
        self.controller.run_until(self.timer.now(), self.queue)

        # process output
        try:
            while True:
                big_step_output = self.queue.get_nowait()
                self.output_callback(big_step_output)
        except queue.Empty:
            pass

        # back to sleep
        next_wakeup = self.controller.next_wakeup()
        if next_wakeup:
            sleep_duration = self.event_loop_convert(next_wakeup - self.controller.simulated_time)
            self.scheduled = self.event_loop.schedule()(sleep_duration, self._wakeup)
        else:
            self.scheduled = None

    def start(self):
        self.timer.start()
        self._wakeup()

    # Uncomment if ever needed:
    # Does not mix well with interrupt().
    # def pause(self):
    #     self.timer.pause()
    #     self.event_loop.cancel()(self.scheduled)

    # Add input. Does not automatically 'wake up' the controller if it is sleeping.
    # If you want the controller to respond immediately, call 'interrupt'.
    def add_input(self, event: Event):
        # If the controller is sleeping, it's simulated time value may be in the past, but we want to make it look like the event arrived NOW, so from the controller's point of view, in the future:
        offset = self.timer.now() - self.controller.simulated_time
        self.controller.add_input(event, offset)

    def interrupt(self):
        if self.scheduled:
            self.event_loop.cancel()(self.scheduled)
        self._wakeup()
