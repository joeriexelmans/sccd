from sccd.realtime.eventloop import *
from sccd.realtime.tkinter import TkInterImplementation
from sccd.cd.parser.xml import *
import GUI
import tkinter
from tkinter.constants import NO

if __name__ == '__main__':
    cd = load_cd("model_microwave.xml")

    def send_event(event: str):
        eventloop.add_input_now(port="in", event_name=event)

    tk = tkinter.Tk()
    tk.withdraw()
    topLevel = tkinter.Toplevel(tk)
    topLevel.resizable(width=NO, height=NO)
    topLevel.title("Microwave oven simulator")
    gui = GUI.GUI(topLevel, send_event)

    def on_output(event):
        if event.port == "out":
            gui.handle_event(event)

    controller = Controller(cd, output_callback=on_output)
    eventloop = EventLoop(controller, TkInterImplementation(tk))

    eventloop.start()
    tk.mainloop()
