'''
Created on 27-jul.-2014

@author: Simon
'''

import Tkinter as tk
import target_py.sccd as sccd
from python_runtime.libs.ui import ui
from python_runtime.statecharts_core import Event
from python_runtime.tkinter_eventloop import *

FIXED_UPDATE_TIME = 20	# ms

if __name__ == '__main__':
	ui.window = tk.Tk()
	ui.window.withdraw()
	controller = sccd.Controller(TkEventLoop(ui.window))
	controller.start()
	ui.window.mainloop()
