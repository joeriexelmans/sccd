from sccd.controller.realtime import *
import tkinter

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

@dataclass
class TkInterImplementation(EventLoopImplementation):
    tk: tkinter.Tk

    def time_unit(self) -> Duration:
        return duration(1, Millisecond)

    def schedule(self) -> Callable[[int, Callable[[],None]], ScheduledID]:
        return self.tk.after

    def cancel(self) -> Callable[[ScheduledID], None]:
        return self.tk.after_cancel

class EventLoop:
    def __init__(self, cd, event_loop, output_callback, time_impl=DefaultTimeImplementation):
        self.timer = Timer(time_impl, unit=cd.globals.delta) # will give us timestamps in model unit
        self.controller = Controller(cd)
        self.event_loop = event_loop
        self.output_callback = output_callback

        self.event_loop_convert = lambda x: int(get_conversion_f(
            cd.globals.delta, event_loop.time_unit())(x)) # got to convert from model unit to eventloop native unit for scheduling

        self.scheduled = None
        self.queue = queue.Queue()

    def _wakeup(self):
        # run controller - output will accumulate in queue
        self.controller.run_until(self.timer.now(), self.queue)

        # process output
        try:
            while True:
                big_step_output = self.queue.get_nowait()
                self.output_callback(big_step_output)
        except queue.Empty:
            pass

        # go to sleep
        # convert our statechart's timestamp to tkinter's (100 us -> 1 ms)
        sleep_duration = self.event_loop_convert(
            self.controller.next_wakeup() - self.controller.simulated_time)
        self.scheduled = self.event_loop.schedule()(sleep_duration, self._wakeup)
        # print("sleeping %d ms" % sleep_duration)

    def start(self):
        self.timer.start()
        self._wakeup()

    def pause(self):
        self.timer.pause()
        self.event_loop.cancel()(self.scheduled)

    # Add input. Does not automatically 'wake up' the controller if it is sleeping.
    # If you want the controller to respond immediately, call 'interrupt'.
    def add_input(self, event):
        offset = self.controller.simulated_time - self.timer.now()
        event.time_offset += offset * self.timer.unit
        self.controller.add_input(event)

    # Do NOT call while paused!
    def interrupt(self):
        self.event_loop.cancel()(self.scheduled)
        self._wakeup()
