'''
Created on 27-jul.-2014

@author: Simon
'''

import Tkinter as tk
import target_py.sccd as sccd
from python_runtime.libs.ui import ui
from python_runtime.statecharts_core import Event
from python_runtime.tkinter_eventloop import *
import threading

if __name__ == '__main__':
    controller = sccd.Controller()
    def raw_inputter():
        while 1:
            controller.addInput(Event(raw_input(), "input", []))
    thread = threading.Thread(target=raw_inputter)
    thread.daemon = True
    thread.start()
    controller.start()