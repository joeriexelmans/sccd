.. _runtime_platforms:

Runtime Platforms
=================
A runtime platform provides the necessary functions for the SCCD kernel to schedule (timed) events. Runtime platforms are implemented in a number of programming languages that can be the target of compilation (at this moment, Python and Javascript are supported). Supporting several runtime platforms is necessary to make SCCD models work in a variety of environments, such as a UI eventloop library or a game engine.

Threads
-------
The ``Threads`` platform is the most basic platform. It runs the SCCD model on the main thread when ``Controller.run()`` is called (meaning that the program will block on this call). If input needs to be provided to the SCCD model or the output of the SCCD model needs to be processed while it's running, a separate thread should be started. For example, the code below shows how input/output works for a compiled SCCD model target_py/target.py which was compiled for the threads platform and has two ports ("input" and "output")::

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
                print output_listener.fetch(-1)
        output_thread = threading.Thread(target=outputter)
        output_thread.daemon = True
        output_thread.start()
        
        controller.start()

Eventloop
---------
The ``Eventloop`` platform works only in combination with a UI system that allows for scheduling events. Default implementations are provided for the Tkinter UI library on Python, and the default scheduler found in Javascript (through the ``setTimeout`` function).

Python
^^^^^^

::
 
    import Tkinter as tk
    import target_py.target as target
    from sccd.runtime.libs.ui import ui
    from sccd.runtime.statecharts_core import Event
    from sccd.runtime.tkinter_eventloop import *

    if __name__ == '__main__':
        ui.window = tk.Tk()
        ui.window.withdraw()
        controller = target.Controller(TkEventLoop(ui.window))
        controller.start()
        ui.window.mainloop()
        
Javascript
^^^^^^^^^^

::

    <script src="https://msdl.uantwerpen.be/git/simon/SCCD/raw/v0.9/src/javascript_sccd_runtime/libs/HackTimer.js"></script>
    <script src="https://msdl.uantwerpen.be/git/simon/SCCD/raw/v0.9/src/javascript_sccd_runtime/statecharts_core.js"></script>
    <script src="https://msdl.uantwerpen.be/git/simon/SCCD/raw/v0.9/src/javascript_sccd_runtime/libs/utils.js"></script>
    <script src="https://msdl.uantwerpen.be/git/simon/SCCD/raw/v0.9/src/javascript_sccd_runtime/libs/svg.js"></script>
    <script src="https://msdl.uantwerpen.be/git/simon/SCCD/raw/v0.9/src/javascript_sccd_runtime/libs/ui.js"></script>
    <script src="target_js/target.js"></script>
    <script>
    controller = new Target.Controller(new JsEventLoop());
    controller.start();
    </script>

Gameloop
--------
The ``Gameloop`` platform works in combination with a game engine, which calls the ``update`` function of the controller at regular intervals.