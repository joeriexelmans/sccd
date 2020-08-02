from sccd.realtime.time import *
from sccd.controller.controller import *
from sccd.util.duration import *
import threading
import queue

# Thread-safe real-time Controller execution in a thread
class ThreadsPlatform:

    def __init__(self, controller: Controller):
        self.controller = controller
        self.timer = Timer(impl=DefaultTimeImplementation, unit=self.controller.cd.get_delta())
        self.lock = threading.Lock()
        self.condition = threading.Condition()

    def create_controller_thread(self) -> threading.Thread:
        def thread():
            # condition object expects fractions of seconds
            to_condition_wait_time = get_conversion_f_float(self.controller.cd.get_delta(), duration(1, Second))

            # keep simulation responsive even if computer cannot keep up
            purposefully_behind = 0

            # simulation starts "now"
            self.timer.start()

            while True:
                # simulate, then sleep:

                with self.lock:
                    self.controller.run_until(self.timer.now() + purposefully_behind) # may take a while
                    next_wakeup = self.controller.next_wakeup()

                if next_wakeup is not None:
                    sleep_duration = next_wakeup - self.timer.now()
                    if sleep_duration < 0:
                        purposefully_behind = sleep_duration
                    else:
                        purposefully_behind = 0
                    with self.condition:
                        self.condition.wait(to_condition_wait_time(sleep_duration))
                else:
                    with self.condition:
                        self.condition.wait()

        return threading.Thread(target=thread)

    def add_input(self, event_name, port, params=[]):
        with self.lock:
            self.controller.add_input(timestamp=self.timer.now(), event_name=event_name, port=port, params=params)
        with self.condition:
            self.condition.notify() # wake up controller thread if sleeping
