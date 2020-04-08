'''
Created on 27-jul.-2014

@author: Simon
'''

import Tkinter as tk
import threading, time
import eventloop_bug
from sccd.runtime.statecharts_core import Event
from sccd.runtime.tkinter_eventloop import *

if __name__ == '__main__':
    window = tk.Tk()
    window.withdraw()
    controller = eventloop_bug.Controller(TkEventLoop(window))
    
    def inputter():
        time.sleep(1)
        while 1:
            controller.addInput(Event("hello world", "input", []))
    for _ in range(2):
        thread = threading.Thread(target=inputter)
        thread.daemon = True
        thread.start()
    
    controller.start()
    window.mainloop()
