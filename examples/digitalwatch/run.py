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
        controller.add_input(
            timestamp=eventloop.now(), event_name=event, port="in", params=[])
        eventloop.interrupt()

    gui.controller.send_event = on_gui_event

    def on_output(event: OutputEvent):
        if event.port == "out":
            # print("out:", e.name)
            # the output event names happen to be functions on our GUI controller:
            method = getattr(gui.controller, event.name)
            method()

    cd = load_cd("model_digitalwatch.xml")

    # from sccd.statechart.static import tree
    # # tree.concurrency_arena_orthogonal( cd.statechart.tree )
    # tree.concurrency_src_dst_orthogonal( cd.statechart.tree )
    # exit()

    controller = Controller(cd, output_callback=on_output)
    eventloop = EventLoop(controller, TkInterImplementation(tk))

    eventloop.start()
    tk.mainloop()

if __name__ == '__main__':
    main()