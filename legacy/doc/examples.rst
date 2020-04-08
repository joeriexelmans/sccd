Examples
========

Timer
-----
This example demonstrates the timed behavior of SCCD. It does not have dynamic structure.

We model a clock which prints the current time every 0.05 seconds. Two clocks are printed: the current wall-clock time and the current simulated time. We expect both to (almost) be the same. The user can interrupt the clock by sending an "interrupt" event. The user can resume the clock by sending a "resume" event.

Threads (Python)
^^^^^^^^^^^^^^^^
In this version, the model sends the current times to an output port, on which the user listens, to print out these times. *self.getSimulatedTime()* and *time()* return the current time in milliseconds, which we have to convert to seconds.

The SCCD model::

    <?xml version="1.0" ?>
    <diagram author="Simon Van Mierlo" name="Timer (Threaded Version)">
        <top>
            from sccd.runtime.accurate_time import time
        </top>
        
        <inport name="input" />        
        <outport name="output" />

        <class name="MainApp" default="true">
            <scxml initial="running">
                <state id="running">
                    <transition target="." after="0.05">
                        <raise event="time_update" port="output">
                            <parameter expr="self.getSimulatedTime()" />
                            <parameter expr="time()" />
                        </raise>
                    </transition>
                    <transition target="../interrupted" event="interrupt" port="input">
                        <raise event="time_update" port="output">
                            <parameter expr="self.getSimulatedTime()" />
                            <parameter expr="time()" />
                        </raise>
                    </transition>
                </state>
                <state id="interrupted">
                    <transition target="." event="interrupt" port="input">
                        <raise event="time_update" port="output">
                            <parameter expr="self.getSimulatedTime()" />
                            <parameter expr="time()" />
                        </raise>
                    </transition>
                    <transition target="../running" event="continue" port="input">
                        <raise event="time_update" port="output">
                            <parameter expr="self.getSimulatedTime()" />
                            <parameter expr="time()" />
                        </raise>
                    </transition>
                </state>
            </scxml>
        </class>
    </diagram>
    
To compile, save this in a file called ``timer.xml`` and run ``python -m sccd.compiler.sccdc -p threads -l python timer.xml``

Then, the following file will run the model::

    import timer
    from sccd.runtime.statecharts_core import Event
    import threading

    if __name__ == '__main__':
        controller = timer.Controller()
        
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
                print "SIMTIME: %.2fs" % (event.getParameters()[0] / 1000.0)
                print "ACTTIME: %.2fs" % (event.getParameters()[1] / 1000.0)
        output_thread = threading.Thread(target=outputter)
        output_thread.daemon = True
        output_thread.start()
        
        controller.start()
        
The time will be printed to the console. The user can send events by typing the string "interrupt" or "continue" in the console.

Eventloop (Python)
^^^^^^^^^^^^^^^^^^
The SCCD model::

    <?xml version="1.0" ?>
    <diagram author="Simon Van Mierlo" name="Timer (Eventloop Version)">
        <top>
            from sccd.runtime.libs.ui import ui
            from sccd.runtime.accurate_time import time
        </top>
        
        <inport name="ui" />

        <class name="MainApp" default="true">
            <method name="MainApp">
                <body>
                    <![CDATA[
                    self.canvas = ui.append_canvas(ui.window,100,100,{'background':'#eee'})
                    self.clock_text = self.canvas.element.create_text(25,25,{'text':'0.0'})
                    self.actual_clock_text = self.canvas.element.create_text(25,50,{'text':'0.0'})
                    interrupt_button = ui.append_button(ui.window, 'INTERRUPT');
                    continue_button = ui.append_button(ui.window, 'CONTINUE');
                    ui.bind_event(interrupt_button.element, ui.EVENTS.MOUSE_CLICK, self.controller, 'interrupt_clicked');
                    ui.bind_event(continue_button.element, ui.EVENTS.MOUSE_CLICK, self.controller, 'continue_clicked');
                    ]]>
                </body>        
            </method>
            <method name="update_timers">
                <body>
                    self.canvas.element.itemconfigure(self.clock_text, text=str('%.2f' % (self.getSimulatedTime() / 1000.0)))
                    self.canvas.element.itemconfigure(self.actual_clock_text, text='%.2f' % (time() / 1000.0))
                </body>
            </method>
            <scxml initial="running">
                <state id="running">
                    <transition target="." after="0.05">
                        <script>
                            self.update_timers()
                        </script>
                    </transition>
                    <transition target="../interrupted" event="interrupt_clicked" port="ui">
                        <script>
                            self.update_timers()
                        </script>
                    </transition>
                </state>
                <state id="interrupted">
                    <transition target="." event="interrupt_clicked" port="ui">
                        <script>
                            self.update_timers()
                        </script>
                    </transition>
                    <transition target="../running" event="continue_clicked" port="ui">
                        <script>
                            self.update_timers()
                        </script>
                    </transition>
                </state>
            </scxml>
        </class>
    </diagram>
    
To compile, save this in a file called ``timer.xml`` and run ``python -m sccd.compiler.sccdc -p eventloop -l python timer.xml``

Then, the following file will run the model::

    import Tkinter as tk
    import timer
    from sccd.runtime.libs.ui import ui
    from sccd.runtime.statecharts_core import Event
    from sccd.runtime.tkinter_eventloop import *

    if __name__ == '__main__':
        ui.window = tk.Tk()

        controller = timer.Controller(TkEventLoop(ui.window))
        controller.start()
        ui.window.mainloop()
        
Eventloop (Javascript)
^^^^^^^^^^^^^^^^^^^^^^
The SCCD model::

    <?xml version="1.0" ?>
    <diagram author="Simon Van Mierlo" name="Timer">
        <inport name="ui" />

        <class name="MainApp" default="true">
            <method name="MainApp">
                <body>
                    <![CDATA[
                    this.canvas = ui.append_canvas(ui.window,400,150,{'background':'#eee'})
                    this.clock_text = this.canvas.add_text(25,25,'0.0')
                    this.actual_clock_text = this.canvas.add_text(25,50,'0.0')
                    var interrupt_button = ui.append_button(ui.window, 'INTERRUPT');
                    var continue_button = ui.append_button(ui.window, 'CONTINUE');
                    ui.bind_event(interrupt_button.element, ui.EVENTS.MOUSE_CLICK, this.controller, 'interrupt_clicked');
                    ui.bind_event(continue_button.element, ui.EVENTS.MOUSE_CLICK, this.controller, 'continue_clicked');
                    ]]>
                </body>
            </method>
            <method name="update_timers">
                <body>
                    this.clock_text.set_text((this.getSimulatedTime() / 1000).toFixed(2));
                    this.actual_clock_text.set_text((this.getSimulatedTime() / 1000).toFixed(2));
                </body>
            </method>
            <scxml initial="running">
                <state id="running">
                    <transition target="." after="0.05">
                        <script>
                            this.update_timers();
                        </script>
                    </transition>
                    <transition target="../interrupted" event="interrupt_clicked" port="ui">
                        <script>
                            this.update_timers();
                        </script>
                    </transition>
                </state>
                <state id="interrupted">
                    <transition target="." event="interrupt_clicked" port="ui">
                        <script>
                            this.update_timers();
                        </script>
                    </transition>
                    <transition target="../running" event="continue_clicked" port="ui">
                        <script>
                            this.update_timers();
                        </script>
                    </transition>
                </state>
            </scxml>
        </class>
    </diagram>
    
To compile, save this in a file called ``timer.xml`` and run ``python -m sccd.compiler.sccdc -p eventloop -l javascript timer.xml``

Then, the following file will run the model::

    <div>
        <script src="https://msdl.uantwerpen.be/git/simon/SCCD/raw/v0.9/src/javascript_sccd_runtime/libs/HackTimer.js"></script>
        <script src="https://msdl.uantwerpen.be/git/simon/SCCD/raw/v0.9/src/javascript_sccd_runtime/statecharts_core.js"></script>
        <script src="https://msdl.uantwerpen.be/git/simon/SCCD/raw/v0.9/src/javascript_sccd_runtime/libs/utils.js"></script>
        <script src="https://msdl.uantwerpen.be/git/simon/SCCD/raw/v0.9/src/javascript_sccd_runtime/libs/svg.js"></script>
        <script src="https://msdl.uantwerpen.be/git/simon/SCCD/raw/v0.9/src/javascript_sccd_runtime/libs/ui.js"></script>
        <script src="timer.js"></script>
        <script>
            controller = new Timer.Controller(new JsEventLoop());
            controller.start();
        </script> 
    </div>
    
Traffic Lights
--------------
The traffic lights example demonstrates most functionality of SCCD. There are three lights (green, yellow, and red). The traffic light autonomously switches between them, but also listens for a police interrupt, which will flash the yellow light. When a second interrupt comes in, the light returns to its last configuration (using a history state).

Python
^^^^^^
The SCCD model::

    <?xml version="1.0" ?>
    <diagram author="Raphael Mannadiar" name="Traffic_Light_Python_Version">
        <top>
            from sccd.runtime.libs.ui import ui
        </top>
        
        <inport name="ui" />

        <class name="MainApp" default="true">
            <relationships>
                <association name="trafficlight" class="TrafficLight" />
            </relationships>
            <method name="MainApp">
                <body>
                    <![CDATA[
                    self.canvas   = ui.append_canvas(ui.window,100,310,{'background':'#eee'});
                    police_button = ui.append_button(ui.window, 'Police interrupt');
                    quit_button   = ui.append_button(ui.window, 'Quit');
                    ui.bind_event(police_button.element, ui.EVENTS.MOUSE_CLICK, self.controller, 'police_interrupt_clicked');
                    ui.bind_event(quit_button.element,      ui.EVENTS.MOUSE_CLICK, self.controller, 'quit_clicked');
                    ]]>
                </body>        
            </method>
            <scxml initial="initializing">
                <state id="initializing">
                    <transition target="../creating">
                        <raise scope="cd" event="create_instance">
                            <parameter expr='"trafficlight"' />
                            <parameter expr='"TrafficLight"' />
                            <parameter expr="self.canvas" />
                        </raise>
                    </transition>
                </state>
                <state id="creating">
                    <transition event="instance_created" target="../initialized">
                        <parameter name="association_name" type="string"/>
                        <raise scope="cd" event="start_instance">
                            <parameter expr="association_name" />
                        </raise>
                        <raise scope="narrow" event="set_association_name" target="association_name">
                            <parameter expr="association_name" />
                        </raise>
                    </transition>
                </state>
                <state id="initialized">
                </state>
            </scxml>
        </class>

        <class name="TrafficLight">
            <relationships>
            </relationships>
            <method name="TrafficLight">
                <parameter name="canvas" />
                <body>
                    <![CDATA[
                    size        = 100;
                    offset      = size+5;
                    self.RED    = 0;
                    self.YELLOW = 1;
                    self.GREEN  = 2;
                    self.colors = ['#f00','#ff0','#0f0']
                    self.lights = [
                        canvas.add_rectangle(size/2, size/2, size, size, {'fill':'#000'}),
                        canvas.add_rectangle(size/2, size/2+offset,     size, size, {'fill':'#000'}),
                        canvas.add_rectangle(size/2, size/2+2*offset, size, size, {'fill':'#000'})];
                    ]]>
                </body>
            </method>
            <method name="clear">
                <body>
                    <![CDATA[
                    self.lights[self.RED].set_color('#000');
                    self.lights[self.YELLOW].set_color('#000');
                    self.lights[self.GREEN].set_color('#000');
                    ]]>
                </body>
            </method>
            <method name="setGreen">
                <body>
                    <![CDATA[
                    self.clear();
                    self.lights[self.GREEN].set_color(self.colors[self.GREEN]);
                    ]]>
                </body>
            </method>
            <method name="setYellow">
                <body>
                    <![CDATA[
                    self.clear();
                    self.lights[self.YELLOW].set_color(self.colors[self.YELLOW]);
                    ]]>
                </body>
            </method>
            <method name="setRed">
                <body>
                    <![CDATA[
                    self.clear();
                    self.lights[self.RED].set_color(self.colors[self.RED]);
                    ]]>
                </body>
            </method>
            <scxml initial="on">
                <state id="on" initial="normal">
                    <state id="normal" initial="red">
                        <state id="red">
                            <onentry>
                                <script>
                                    <![CDATA[
                                    self.setRed();
                                    ]]>
                                </script>
                            </onentry>
                            <transition after='3' target='../green'/>
                        </state>
                        <state id="green">
                            <onentry>
                                <script>
                                    <![CDATA[
                                    self.setGreen();
                                    ]]>
                                </script>
                            </onentry>
                            <transition after='2' target='../yellow'/>
                        </state>
                        <state id="yellow">
                            <onentry>
                                <script>
                                    <![CDATA[
                                    self.setYellow();
                                    ]]>
                                </script>
                            </onentry>
                        <transition after='1' target='../red'/>
                        </state>
                        <transition event='police_interrupt_clicked' port='ui' target='../interrupted'/>
                        <history id="history"/>
                    </state>
                    <state id="interrupted" initial="yellow">
                        <state id="yellow">
                            <onentry>
                                <script>
                                    <![CDATA[
                                    self.setYellow();
                                    ]]>
                                </script>
                            </onentry>
                            <transition after='.5' target='../black'/>
                        </state>
                        <state id="black">
                            <onentry>
                                <script>
                                    <![CDATA[
                                    self.clear();
                                    ]]>
                                </script>
                            </onentry>
                            <transition after='.5' target='../yellow'/>
                        </state>
                        <transition event='police_interrupt_clicked' port='ui' target='../normal/history'/>
                    </state>
                    <transition event='quit_clicked' port='ui' target='../off'/>
                </state>
                <state id="off">
                    <onentry>
                        <script>
                            <![CDATA[
                            self.clear();
                            ]]>
                        </script>
                    </onentry>
                </state>
            </scxml>
        </class>
    </diagram>
    
To compile, save this in a file called ``trafficlight.xml`` and run ``python -m sccd.compiler.sccdc -p eventloop -l python trafficlight.xml``

Then, the following file will run the model::

    import Tkinter as tk
    import trafficlight
    from sccd.runtime.libs.ui import ui
    from sccd.runtime.statecharts_core import Event
    from sccd.runtime.tkinter_eventloop import *

    if __name__ == '__main__':
        ui.window = tk.Tk()

        controller = trafficlight.Controller(TkEventLoop(ui.window))
        controller.start()
        ui.window.mainloop()
        
Javascript
^^^^^^^^^^
The SCCD model::

    <?xml version="1.0" ?>
    <diagram author="Raphael Mannadiar" name="Traffic_Light_JavaScript_Version">
        <inport name="ui" />

        <class name="MainApp" default="true">
            <relationships>
                <association name="trafficlight" class="TrafficLight" />
            </relationships>
            <method name="MainApp">
                <body>
                    <![CDATA[
                    this.canvas	= ui.append_canvas(ui.window,100,310,{'background':'#eee'});
                    var police_button = ui.append_button(ui.window, 'Police interrupt');
                    var quit_button	= ui.append_button(ui.window, 'Quit');
                    ui.bind_event(police_button.element, ui.EVENTS.MOUSE_CLICK, this.controller, 'police_interrupt_clicked');
                    ui.bind_event(quit_button.element, 	 ui.EVENTS.MOUSE_CLICK, this.controller, 'quit_clicked');
                    ]]>
                </body>		
            </method>
            <scxml initial="initializing">
                <state id="initializing">
                    <transition target="../creating">
                        <raise scope="cd" event="create_instance">
                            <parameter expr='"trafficlight"' />
                            <parameter expr='"TrafficLight"' />
                            <parameter expr="this.canvas" />
                        </raise>
                    </transition>
                </state>
                <state id="creating">
                    <transition event="instance_created" target="../initialized">
                        <parameter name="association_name" type="string"/>
                        <raise scope="cd" event="start_instance">
                            <parameter expr="association_name" />
                        </raise>
                        <raise scope="narrow" event="set_association_name" target="association_name">
                            <parameter expr="association_name" />
                        </raise>
                    </transition>
                </state>
                <state id="initialized">
                </state>
            </scxml>
        </class>

        <class name="TrafficLight">
            <relationships>
            </relationships>
            <method name="TrafficLight">
                <parameter name="canvas" />
                <body>
                    <![CDATA[
                    var size 	= 100;
                    var offset 	= size+5;
                    this.RED 	= 0;
                    this.YELLOW = 1;
                    this.GREEN 	= 2;
                    this.colors	= ['#f00','#ff0','#0f0']
                    this.lights = [canvas.add_rectangle(size/2, size/2, 		 	 size, size, {'fill':'#000'}),
                                        canvas.add_rectangle(size/2, size/2+offset,	 size, size, {'fill':'#000'}),
                                        canvas.add_rectangle(size/2, size/2+2*offset, size, size, {'fill':'#000'})];
                    ]]>
                </body>
            </method>
            <method name="clear">
                <body>
                    <![CDATA[
                    this.lights[this.RED].set_color('#000');
                    this.lights[this.YELLOW].set_color('#000');
                    this.lights[this.GREEN].set_color('#000');
                    ]]>
                </body>
            </method>
            <method name="setGreen">
                <body>
                    <![CDATA[
                    this.clear();
                    this.lights[this.GREEN].set_color(this.colors[this.GREEN]);
                    ]]>
                </body>
            </method>
            <method name="setYellow">
                <body>
                    <![CDATA[
                    this.clear();
                    this.lights[this.YELLOW].set_color(this.colors[this.YELLOW]);
                    ]]>
                </body>
            </method>
            <method name="setRed">
                <body>
                    <![CDATA[
                    this.clear();
                    this.lights[this.RED].set_color(this.colors[this.RED]);
                    ]]>
                </body>
            </method>
            <scxml initial="on">
                <state id="on" initial="normal">
                    <state id="normal" initial="red">
                        <state id="red">
                            <onentry>
                                <script>
                                    <![CDATA[
                                    this.setRed();
                                    ]]>
                                </script>
                            </onentry>
                            <transition after='3' target='../green'/>
                        </state>
                        <state id="green">
                            <onentry>
                                <script>
                                    <![CDATA[
                                    this.setGreen();
                                    ]]>
                                </script>
                            </onentry>
                            <transition after='2' target='../yellow'/>
                        </state>
                        <state id="yellow">
                            <onentry>
                                <script>
                                    <![CDATA[
                                    this.setYellow();
                                    ]]>
                                </script>
                            </onentry>
                        <transition after='1' target='../red'/>
                        </state>
                        <transition event='police_interrupt_clicked' port='ui' target='../interrupted'/>
                        <history id="history"/>
                    </state>
                    <state id="interrupted" initial="yellow">
                        <state id="yellow">
                            <onentry>
                                <script>
                                    <![CDATA[
                                    this.setYellow();
                                    ]]>
                                </script>
                            </onentry>
                            <transition after='.5' target='../black'/>
                        </state>
                        <state id="black">
                            <onentry>
                                <script>
                                    <![CDATA[
                                    this.clear();
                                    ]]>
                                </script>
                            </onentry>
                            <transition after='.5' target='../yellow'/>
                        </state>
                        <transition event='police_interrupt_clicked' port='ui' target='../normal/history'/>
                    </state>
                    <transition event='quit_clicked' port='ui' target='../off'/>
                </state>
                <state id="off">
                    <onentry>
                        <script>
                            <![CDATA[
                            this.clear();
                            ]]>
                        </script>
                    </onentry>
                </state>
            </scxml>
        </class>
    </diagram>
    
To compile, save this in a file called ``trafficlight.xml`` and run ``python -m sccd.compiler.sccdc -p eventloop -l javascript trafficlight.xml``

Then, the following file will run the model::

    <div>
        <script src="https://msdl.uantwerpen.be/git/simon/SCCD/raw/v0.9/src/javascript_sccd_runtime/libs/HackTimer.js"></script>
        <script src="https://msdl.uantwerpen.be/git/simon/SCCD/raw/v0.9/src/javascript_sccd_runtime/statecharts_core.js"></script>
        <script src="https://msdl.uantwerpen.be/git/simon/SCCD/raw/v0.9/src/javascript_sccd_runtime/libs/utils.js"></script>
        <script src="https://msdl.uantwerpen.be/git/simon/SCCD/raw/v0.9/src/javascript_sccd_runtime/libs/svg.js"></script>
        <script src="https://msdl.uantwerpen.be/git/simon/SCCD/raw/v0.9/src/javascript_sccd_runtime/libs/ui.js"></script>
        <script src="trafficlight.js"></script>
        <script>
        controller = new Traffic_Light_JavaScript_Version.Controller(new JsEventLoop());
        controller.start();
        </script> 
    </div>
