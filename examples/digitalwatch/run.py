from DigitalWatchGUI import DigitalWatchGUI
import tkinter
from tkinter.constants import NO
from time import perf_counter
from sccd.controller.controller import *
from sccd.statechart.parser.xml import parse_f, statechart_parser_rules
from sccd.model.model import *
import queue

def now():
    return int(perf_counter()*10000) # 100 us-precision, same as our model delta

def main():
    g = Globals()
    sc_rules = statechart_parser_rules(g, "statechart_digitalwatch.xml")
    statechart = parse_f("statechart_digitalwatch.xml", rules=sc_rules)
    model = SingleInstanceModel(g, statechart)
    g.set_delta(duration(100, Microsecond))
    controller = Controller(model)

    scheduled = None

    def gui_event(event: str):
        print(event)
        controller.add_input(InputEvent(name=event, port="in", params=[], time_offset=duration(0)))
        if scheduled:
            tk.after_cancel(scheduled)
        wakeup()

    tk = tkinter.Tk()
    tk.withdraw()
    topLevel = tkinter.Toplevel(tk)
    topLevel.resizable(width=NO, height=NO)
    topLevel.title("DWatch")
    gui = DigitalWatchGUI(topLevel)
    gui.controller.send_event = gui_event

    q = queue.Queue()
    start_time = now()

    def wakeup():
        nonlocal scheduled
        # run controller - output will accumulate in 'q'
        controller.run_until(now() - start_time, q)

        # process output
        try:
            while True:
                big_step_output = q.get_nowait()
                for e in big_step_output:
                    print("out:", e.name)
                    # print("got output:", e.name)
                    # the output event names happen to be functions on our GUI controller:
                    method = getattr(gui.controller, e.name)
                    # print(method)
                    method()
        except queue.Empty:
            pass

        # done enough for now, go to sleep
        # convert our statechart's timestamp to tkinter's (100 us -> 1 ms)
        sleep_duration = (controller.next_wakeup() - controller.simulated_time) // 10
        scheduled = tk.after(sleep_duration, wakeup)

    tk.after(0, wakeup)
    tk.mainloop()

if __name__ == '__main__':
    main()