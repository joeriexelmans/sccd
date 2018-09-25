import target_py.target as target
from sccd.runtime.statecharts_core import Event
import threading

if __name__ == '__main__':
    controller = target.Controller()
    
    def raw_inputter():
        while 1:
            controller.addInput(Event(raw_input(), "input", []))
    input_thread = threading.Thread(target=raw_inputter)
    input_thread.daemon = True
    input_thread.start()
    
    output_listener = controller.addOutputListener(["output"])
    def outputter():
        while 1:
            event = output_listener.fetch(-1)
            print event
            print "SIMTIME: %.2fs" % (event.getParameters()[0] / 1000.0)
            print "ACTTIME: %.2fs" % (event.getParameters()[1] / 1000.0)
    output_thread = threading.Thread(target=outputter)
    output_thread.daemon = True
    output_thread.start()
    
    controller.start()