'''
Created on 27-jul.-2014

@author: Simon
'''

import Tkinter as tk
import target_py.target_performance as target
from sccd.runtime.libs.ui import ui
from sccd.runtime.statecharts_core import Event
from sccd.runtime.tkinter_eventloop import *

if __name__ == '__main__':
    ui.window = tk.Tk()
    ui.window.withdraw()
    def callback(ctrl, behind_schedule):
        if behind_schedule > 2000:
            print len(ctrl.object_manager.instances)
            ctrl.stop()
            ui.window.destroy()
    controller = target.Controller(TkEventLoop(ui.window), behind_schedule_callback=callback)
    controller.start()
    ui.window.mainloop()
