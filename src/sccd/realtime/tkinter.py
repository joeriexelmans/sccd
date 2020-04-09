from dataclasses import dataclass
from sccd.realtime.eventloop import EventLoopImplementation
import tkinter
from sccd.util.duration import *

@dataclass
class TkInterImplementation(EventLoopImplementation):
    tk: tkinter.Tk

    def time_unit(self):
        return duration(1, Millisecond)

    def schedule(self):
        return self.tk.after

    def cancel(self):
        return self.tk.after_cancel
