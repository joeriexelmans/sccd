from statecharts_core import EventLoop
import math
from accurate_time import time

class TkEventLoop(EventLoop):
    def __init__(self, tk):
        self.ctr = 0

        # bind scheduler callback
        def schedule(callback, timeout, behind = False):
            if behind:
                tk.update_idletasks()
            return tk.after(int(math.ceil(timeout * 1000.0)), callback)

        EventLoop.__init__(self, schedule, tk.after_cancel)

