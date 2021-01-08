from sccd.realtime.eventloop import *
from sccd.realtime.tkinter import TkInterImplementation
from sccd.cd.parser.xml import *

def main():
    import tkinter
    from tkinter.constants import NO
    from DigitalWatchGUI import DigitalWatchGUI

    tk = tkinter.Tk()
    tk.withdraw()
    topLevel = tkinter.Toplevel(tk)
    topLevel.resizable(width=NO, height=NO)
    topLevel.title("DWatch")
    gui = DigitalWatchGUI(topLevel)

    def on_gui_event(event: str):
        eventloop.add_input_now(port="in", event_name=event)

    gui.controller.send_event = on_gui_event

    def on_output(event: OutputEvent):
        # if event.port == "out":
            # print("out:", e.name)
            # the output event names happen to be functions on our GUI controller:
        method = getattr(gui.controller, event.name, None)
        if method is not None:
            method()

    cd = load_cd("../common/digitalwatch.xml")

    controller = Controller(cd, output_callback=on_output)
    eventloop = EventLoop(controller, TkInterImplementation(tk))

    eventloop.start() # Just marks the current wall-clock time as "time zero", and schedules the first controller wakeup with Tk.
    tk.mainloop() # This actually runs Tk's eventloop in the current thread, with our own event loop interleaved.

if __name__ == '__main__':
    main()