'''
Created on 27-jul.-2014

@author: Simon
'''

import threading

import Tkinter as tk
import sccd_no_ui as target
from sccd.runtime.libs.ui import ui
from sccd.runtime.statecharts_core import Event
from sccd.runtime.tkinter_eventloop import *
from ui_classes import *
from widget_private_ports import Widget

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()

#    def add_event(*args):
#        print "okay adding %s" % args
#
#    root.bind("<<ADD_EVENT>>", add_event)
#
#    controller = target.Controller(TkEventLoop(root))
#
#    def raw_inputter():
#        while 1:
#            #controller.addInput(Event(raw_input(), "input", []))
#            root.event_generate("<<ADD_EVENT>>")
#    input_thread = threading.Thread(target=raw_inputter)
#    input_thread.daemon = True
#    input_thread.start()
    
#    output_listener = controller.addOutputListener(["ui_out"])
#    def outputter():
#        while 1:
#            event = output_listener.fetch(-1)
#            print event
#    output_thread = threading.Thread(target=outputter)
#    output_thread.daemon = True
#    output_thread.start()

    controller = target.Controller(TkEventLoop(root))
    Widget.controller = controller

    listener = controller.addOutputListener(controller.output_ports["ui_out"])
    windows = {}
    def check_output():
        while True:
            output_event = listener.fetch(0)
            if not output_event is None:
                if output_event.getName() == "create_new_window":
                    assoc_name = output_event.getParameters()[0]
                    sccd_object = output_event.getParameters()[1]
                    windows[assoc_name] = WindowVis(sccd_object)
                elif output_event.getName() == "delete_window":
                    assoc_name = output_event.getParameters()[0]
                    windows[assoc_name].destruct()
                    del windows[assoc_name]
                elif output_event.getName() == "stop_ui":
                    root.quit()
            else:
                break
        root.after(40, check_output) # hmm yeah so this delay is problematic: the visualization is created a bit AFTER the statechart object is, which means that the output listener is created too late, which means events are getting lost
    root.after(40, check_output)

    controller.start()
    root.mainloop()
