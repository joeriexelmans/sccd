from dataclasses import dataclass
from sccd.realtime.eventloop import EventLoopImplementation
import tkinter
from sccd.util.duration import *

@dataclass
class TkInterImplementation(EventLoopImplementation):
    tk: tkinter.Tk

    def time_unit(self):
        return duration(1, Millisecond)

    def schedule(self, timeout, callback):
        id = self.tk.after(timeout, callback)
        # Unlike, say, your browser's JavaScript event loop, TkInter only does certain jobs it considers less urgent, like rendering widgets, when it is idle. As a result, the GUI would hang if the simulation cannot keep up with wallclock time. The solution is to force Tk to do these jobs regularly.
        # It may seem overkill to call update_idletasks with every 'schedule' operation, but it isn't: Our event loop integration automatically makes fewer 'schedule' calls per amount of simulated time when the CPU is busy. With each "wakeup", we uninterruptably (but guaranteed to end) simulate all the way up to the wallclock time of the beginning of the wakeup. Only when this is done, (and by the time this is done, we may be "behind" again, we don't care), do we schedule another wakeup, and at the same time, force Tk's idle tasks to run.
        # It's a beautiful, self-balancing solution. A real serendipity.
        self.tk.update_idletasks()
        return id

    def cancel(self, id):
        self.tk.after_cancel(id)
