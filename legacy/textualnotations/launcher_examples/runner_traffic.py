'''
Created on 18 Aug 2014

@author: Raphael
'''

import Tkinter as tk
import traffic
from python_runtime.libs.ui import ui
from python_runtime.statecharts_core import Event


FIXED_UPDATE_TIME = 20	#ms


def update(controller,window):
    controller.update(FIXED_UPDATE_TIME/1000.0)
    window.after(FIXED_UPDATE_TIME,update,controller,window)


if __name__ == '__main__':
    ui.window = tk.Tk()
    controller = traffic.Controller()
    controller.start()
    update(controller,ui.window)
    ui.window.mainloop()				
