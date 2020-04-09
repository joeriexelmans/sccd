from sccd.statechart.parser.xml import parse_f, statechart_parser_rules
from sccd.cd.cd import *
from sccd.realtime.eventloop import *
from sccd.realtime.tkinter import TkInterImplementation
import queue

def main():
    # Load statechart
    g = Globals()
    sc_rules = statechart_parser_rules(g, "statechart_digitalwatch.xml")
    statechart = parse_f("statechart_digitalwatch.xml", rules=sc_rules)
    cd = SingleInstanceCD(g, statechart)
    g.set_delta(duration(100, Microsecond))


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
        eventloop.add_input(Event(id=-1, name=event, port="in", params=[]))
        eventloop.interrupt()

    gui.controller.send_event = on_gui_event

    def on_big_step(output):
        for e in output:
            # print("out:", e.name)
            # the output event names happen to be functions on our GUI controller:
            method = getattr(gui.controller, e.name)
            method()

    eventloop = EventLoop(cd, TkInterImplementation(tk), on_big_step)

    eventloop.start()
    tk.mainloop()

if __name__ == '__main__':
    main()