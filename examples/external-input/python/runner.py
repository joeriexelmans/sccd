import test, threading
from sccd.runtime.statecharts_core import Event

controller = test.Controller(False)
def raw_inputter():
    while 1:
        controller.addInput(Event(raw_input(), "input", []))
thread = threading.Thread(target=raw_inputter)
thread.daemon = True
thread.start()
controller.start()
