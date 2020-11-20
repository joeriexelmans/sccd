from sccd.realtime.eventloop import *
from sccd.realtime.tkinter import TkInterImplementation
from sccd.cd.parser.xml import *
import GUI
import sys

if __name__ == '__main__':
    if len(sys.argv) == 2:
        model_path = sys.argv[1]
    else:
        model_path = "models/model_03_orthogonal.xml"

    cd = load_cd(model_path)

    def send_event(event: str):
        eventloop.add_input_now(port="in", event_name=event)

    GUI.gui.send_event = send_event

    def on_output(event):
        if event.port == "out":
            GUI.gui.handle_event(event)

    controller = Controller(cd, output_callback=on_output)
    eventloop = EventLoop(controller, TkInterImplementation(GUI.tk))

    eventloop.start()
    GUI.tk.mainloop()
