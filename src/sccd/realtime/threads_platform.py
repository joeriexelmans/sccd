from sccd.realtime.time import *
from sccd.controller.controller import *
from sccd.util.duration import *
import threading

# Thread-safe real-time Controller execution in a thread
class ThreadsPlatform:

    def __init__(self, controller: Controller):
        self.controller = controller
        self.timer = Timer(impl=DefaultTimeImplementation, unit=self.controller.cd.get_delta())
        self.lock = threading.Lock() # A queue would also work, but because of Python's GIL, a queue would not perform better.
        self.condition = threading.Condition()

        # keep simulation responsive even if computer cannot keep up
        self.purposefully_behind = 0

    def create_controller_thread(self) -> threading.Thread:
        def thread():
            # condition object expects fractions of seconds
            to_condition_wait_time = get_conversion_f_float(self.controller.cd.get_delta(), duration(1, Second))


            # simulation starts "now" (wall-clock time)
            self.timer.start()

            while True:
                with self.lock:
                    self.controller.run_until(self.timer.now() + self.purposefully_behind) # may take a while
                    next_wakeup = self.controller.next_wakeup()

                if next_wakeup is not None:
                    sleep_duration = next_wakeup - self.timer.now()
                    if sleep_duration < 0:
                        self.purposefully_behind = sleep_duration
                        sleep_duration = 0
                    else:
                        self.purposefully_behind = 0
                    with self.condition:
                        self.condition.wait(to_condition_wait_time(sleep_duration))
                else:
                    with self.condition:
                        self.condition.wait()

        return threading.Thread(target=thread)

    def now(self):
        return self.timer.now() + self.purposefully_behind

    # Add an input event with timestamp "now" (wall-clock time)
    # Safe to call this method from any thread.
    def add_input_now(self, port, event_name, params=[]):
        with self.lock:
            self.controller.add_input(timestamp=self.timer.now(), port=port, event_name=event_name, params=params)
        with self.condition:
            self.condition.notify() # wake up controller thread if sleeping
