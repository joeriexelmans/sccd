from sccd.cd.parser.xml import *
from sccd.controller.controller import *
import threading
import queue
from sccd.realtime.eventloop import *
from sccd.realtime.tkinter import *

def main():
    cd = load_cd("model_chatclient.xml")

    def on_output(event: OutputEvent):
        if event.port == "network":
            network.add_input(event.name, event.params)

    from lib import ui, network_client

    controller = Controller(cd, output_callback=on_output)
    eventloop = ThreadSafeEventLoop(controller, TkInterImplementation(ui.window))

    ui.init(eventloop)
    network = network_client.NetworkClient(eventloop)

    # This starts the network client in a new thread.
    network.start()

    # This only sets the 'start time' to the current wall-clock time, initializes the statechart and lets it run for a bit (in this thread) if there are already due events (events with timestamp zero). Then returns.
    eventloop.start()

    # This takes control of the current thread and runs tk's event loop in it.
    ui.window.mainloop()

if __name__ == '__main__':
    main()