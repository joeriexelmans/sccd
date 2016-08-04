'''
Created on 27-jul.-2014

@author: Simon
'''

import Tkinter as tk
import target_py.target as target
from sccd.runtime.statecharts_core import Event
import threading

if __name__ == '__main__':
    controller = target.Controller()
    def raw_inputter():
        while 1:
            controller.addInput(Event(raw_input(), "input", []))
    thread = threading.Thread(target=raw_inputter)
    thread.daemon = True
    thread.start()
    controller.start()