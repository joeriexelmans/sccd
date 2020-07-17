"""
Runner script for the TkInter chat window SCCD model.

Author: Yentl Van Tendeloo
"""

import Tkinter as tk
import chatclient
import socket2event
from python_runtime.statecharts_core import Event
from python_runtime.tkinter_eventloop import *
from chatwindowGUI import ChatWindowGUI

def keypress(key):
    global controller
    try:
        str(key.char)
        if len(key.char) == 1:
            controller.addInput(Event("input", "tkinter_input", [key.char]), 0.0)
        # Don't do anything for empty characters, as these are control characters (e.g. press shift)
    except UnicodeEncodeError:
        print("Unicode input is not supported for simplicity")

root = ChatWindowGUI(keypress)
		
if __name__ == "__main__":
    global controller
    controller = chatclient.Controller(root, TkEventLoop(root))
    socket2event.boot_translation_service(controller)
    controller.start()
    try:
		root.mainloop()
    except:
        controller.stop()
