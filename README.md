Statecharts and Class Diagram Compiler
======================================

Installation
-------------
Within the `src` directory, execute `python setup.py install --user`.

Compiling SCCDXML Files
-------------
To compile a conforming SCCDXML file, the provided Python compiler can be used:
```sh
$python -m sccd.compiler.sccdc --help
usage: python -m sccd.compiler.sccdc [-h] [-o OUTPUT] [-v VERBOSE]
                                     [-p PLATFORM] [-l LANGUAGE]
                                     input

positional arguments:
  input                 The path to the XML file to be compiled.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        The path to the generated code. Defaults to the same
                        name as the input file but with matching extension.
  -v VERBOSE, --verbose VERBOSE
                        2 = all output; 1 = only warnings and errors; 0 = only
                        errors; -1 = no output. Defaults to 2.
  -p PLATFORM, --platform PLATFORM
                        Let the compiled code run on top of threads, gameloop
                        or eventloop. The default is eventloop.
  -l LANGUAGE, --language LANGUAGE
                        Target language, either "javascript" or "python".
                        Defaults to the latter.
```

The Threads Platform
-------------
The `Threads` platform is the most basic platform. It runs the SCCD model on the main thread when `Controller.run()` is called (meaning that the program will block on this call). If input needs to be provided to the SCCD model or the output of the SCCD model needs to be processed while it's running, a separate thread should be started. For example, the code below shows how input/output works for a compiled SCCD model `target_py/target.py` which was compiled for the `threads` platform and has two ports ("input" and "output"):
```python
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
```

The Eventloop Platform
-------------
The `Eventloop` platform works only in combination with a UI system that allows for scheduling events. Default implementations are provided for the Tkinter UI library on Python, and the default scheduler found in Javascript (through the `setTimeout` function).

In Python:
```python
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
```

In Javascript:
```javascript
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
```

The Gameloop Platform
-------------
The `Gameloop` platform works in combination with a game engine, which calls the `update` function of the controller at regular intervals.

Examples
-------------
A number of examples can be found in the `examples` folder, demonstrating the syntax and capabilities of SCCD. They can be compiled by executing `make clean all` inside the `examples` folder. Each example has an associated runner file, with which the example can be executed.

Tests
-------------
A number of tests are provided which make sure the compiler and runtime implement the correct behaviour. They can be compiled by executing `make clean all` inside the `tests` folder. Tests are compiled for both Python and Javascript.

The generated Python test cases (in the `tests/target_py` folder) can be run by executing `run_tests.py` inside the `tests` folder.

The generated Javascript test cases (in the `tests/target_js` folder) can be run by executing `run_tests.html` inside the `tests` folder.