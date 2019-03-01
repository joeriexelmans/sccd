'''
Created on 27-jul.-2014

@author: Simon
'''

import Tkinter as tk
import target_py.multiwindow as target
from sccd.runtime.statecharts_core import Event
from sccd.runtime.tkinter_eventloop import *
from widget import Widget

if __name__ == '__main__':
    window = tk.Tk()
    window.withdraw()
    controller = target.Controller(window, TkEventLoop(window))
    Widget.controller = controller
    controller.start()
    window.mainloop()
