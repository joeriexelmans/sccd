import sys
sys.path.append("../")

import tester
import Tkinter as tk
import threading
import time
from sccd.runtime.tkinter_eventloop import *
from sccd.runtime.statecharts_core import Event

from sccd_widget import SCCDWidget

class Root(tk.Tk, SCCDWidget):
    def __init__(self):
        tk.Tk.__init__(self)
        SCCDWidget.__init__(self)

def send_input(controller):
    while 1:
        controller.addInput(Event("evt", "input", []))
        time.sleep(0.01)

if __name__ == '__main__':
    root = Root()
    controller = tester.Controller(TkEventLoop(root))
    SCCDWidget.controller = controller
    controller.start()

    for _ in range(50):
        thrd = threading.Thread(target=send_input, args=[controller])
        thrd.daemon = True
        thrd.start()

    root.mainloop()
