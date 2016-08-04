/**
 * Statechart compiler by Glenn De Jonghe
 * Javascript generator by Joeri Exelmans
 * 
 * Date:   Tue Sep 09 17:59:36 2014
 * 
 * Model author: Raphael Mannadiar
 * Model name:   Traffic_Light
 * Model description:
    PIM Traffic lights.
 */

// put everything in an object (serves as "namespace")
Traffic_Light = {};

// closure scope
(function() {

// The actual constructor
var TrafficLight = function(controller, canvas) {
    // Unique IDs for all statechart nodes
    this.Root = 0;
    this.Root_on = 1;
    this.Root_on_interrupted = 2;
    this.Root_on_normal = 3;
    this.Root_on_interrupted_yellow = 4;
    this.Root_on_interrupted_black = 5;
    this.Root_on_normal_yellow = 6;
    this.Root_on_normal_green = 7;
    this.Root_on_normal_red = 8;
    this.Root_off = 9;
    
    TrafficLight.prototype.commonConstructor.call(this,controller);
    
    // constructor body (user-defined)
    var size = 100;
    var offset = size + 5;
    this.RED = 0;
    this.YELLOW = 1;
    this.GREEN = 2;
    this.colors = ['#f00', '#ff0', '#0f0'];
    this.lights = [canvas.add_rectangle(size / 2, size / 2, size, size, {'fill':'#000'}), canvas.add_rectangle(size / 2, size / 2 + offset, size, size, {'fill':'#000'}), canvas.add_rectangle(size / 2, size / 2 + 2 * offset, size, size, {'fill':'#000'})];
};


TrafficLight.prototype = new RuntimeClassBase();

// User defined method
TrafficLight.prototype.setYellow = function() {
    this.clear();
    this.lights[this.YELLOW].set_color(this.colors[this.YELLOW]);
    
};
// User defined method
TrafficLight.prototype.setGreen = function() {
    this.clear();
    this.lights[this.GREEN].set_color(this.colors[this.GREEN]);
    
};
// User defined method
TrafficLight.prototype.clear = function() {
    this.lights[this.RED].set_color('#000');
    this.lights[this.YELLOW].set_color('#000');
    this.lights[this.GREEN].set_color('#000');
    
};
// User defined method
TrafficLight.prototype.setRed = function() {
    this.clear();
    this.lights[this.RED].set_color(this.colors[this.RED]);
    
};
// Statechart enter/exit action method(s) :

TrafficLight.prototype.enter_Root_on = function() {
    this.current_state[this.Root].push(this.Root_on);
};

TrafficLight.prototype.exit_Root_on = function() {
    if (this.current_state[this.Root_on].indexOf(this.Root_on_interrupted) !== -1) {
        this.exit_Root_on_interrupted();
    }
    if (this.current_state[this.Root_on].indexOf(this.Root_on_normal) !== -1) {
        this.exit_Root_on_normal();
    }
    this.current_state[this.Root] = new Array();
};

TrafficLight.prototype.enter_Root_on_interrupted = function() {
    this.current_state[this.Root_on].push(this.Root_on_interrupted);
};

TrafficLight.prototype.exit_Root_on_interrupted = function() {
    if (this.current_state[this.Root_on_interrupted].indexOf(this.Root_on_interrupted_yellow) !== -1) {
        this.exit_Root_on_interrupted_yellow();
    }
    if (this.current_state[this.Root_on_interrupted].indexOf(this.Root_on_interrupted_black) !== -1) {
        this.exit_Root_on_interrupted_black();
    }
    this.current_state[this.Root_on] = new Array();
};

TrafficLight.prototype.enter_Root_on_normal = function() {
    this.current_state[this.Root_on].push(this.Root_on_normal);
};

TrafficLight.prototype.exit_Root_on_normal = function() {
    this.history_state[this.Root_on_normal] = this.current_state[this.Root_on_normal];
    if (this.current_state[this.Root_on_normal].indexOf(this.Root_on_normal_yellow) !== -1) {
        this.exit_Root_on_normal_yellow();
    }
    if (this.current_state[this.Root_on_normal].indexOf(this.Root_on_normal_green) !== -1) {
        this.exit_Root_on_normal_green();
    }
    if (this.current_state[this.Root_on_normal].indexOf(this.Root_on_normal_red) !== -1) {
        this.exit_Root_on_normal_red();
    }
    this.current_state[this.Root_on] = new Array();
};

TrafficLight.prototype.enter_Root_on_interrupted_yellow = function() {
    this.timers[0] = 0.5 * 1000.0; /* convert ms to s */
    this.setYellow();
    this.current_state[this.Root_on_interrupted].push(this.Root_on_interrupted_yellow);
};

TrafficLight.prototype.exit_Root_on_interrupted_yellow = function() {
    delete this.timers[0];
    this.current_state[this.Root_on_interrupted] = new Array();
};

TrafficLight.prototype.enter_Root_on_interrupted_black = function() {
    this.timers[1] = 0.5 * 1000.0; /* convert ms to s */
    this.clear();
    this.current_state[this.Root_on_interrupted].push(this.Root_on_interrupted_black);
};

TrafficLight.prototype.exit_Root_on_interrupted_black = function() {
    delete this.timers[1];
    this.current_state[this.Root_on_interrupted] = new Array();
};

TrafficLight.prototype.enter_Root_on_normal_yellow = function() {
    this.timers[2] = 1.0 * 1000.0; /* convert ms to s */
    this.setYellow();
    this.current_state[this.Root_on_normal].push(this.Root_on_normal_yellow);
};

TrafficLight.prototype.exit_Root_on_normal_yellow = function() {
    delete this.timers[2];
    this.current_state[this.Root_on_normal] = new Array();
};

TrafficLight.prototype.enter_Root_on_normal_green = function() {
    this.timers[3] = 2.0 * 1000.0; /* convert ms to s */
    this.setGreen();
    this.current_state[this.Root_on_normal].push(this.Root_on_normal_green);
};

TrafficLight.prototype.exit_Root_on_normal_green = function() {
    delete this.timers[3];
    this.current_state[this.Root_on_normal] = new Array();
};

TrafficLight.prototype.enter_Root_on_normal_red = function() {
    this.timers[4] = 3.0 * 1000.0; /* convert ms to s */
    this.setRed();
    this.current_state[this.Root_on_normal].push(this.Root_on_normal_red);
};

TrafficLight.prototype.exit_Root_on_normal_red = function() {
    delete this.timers[4];
    this.current_state[this.Root_on_normal] = new Array();
};

TrafficLight.prototype.enter_Root_off = function() {
    this.clear();
    this.current_state[this.Root].push(this.Root_off);
};

TrafficLight.prototype.exit_Root_off = function() {
    this.current_state[this.Root] = new Array();
};

// Statechart enter/exit default method(s) :

TrafficLight.prototype.enterDefault_Root_on = function() {
    this.enter_Root_on();
    this.enterDefault_Root_on_normal();
};

TrafficLight.prototype.enterDefault_Root_on_interrupted = function() {
    this.enter_Root_on_interrupted();
    this.enter_Root_on_interrupted_yellow();
};

TrafficLight.prototype.enterDefault_Root_on_normal = function() {
    this.enter_Root_on_normal();
    this.enter_Root_on_normal_red();
};

// Statechart enter/exit history method(s) :

TrafficLight.prototype.enterHistoryShallow_Root_on_normal = function() {
    if (this.history_state[this.Root_on_normal].length === 0) {
        this.enter_Root_on_normal_red();
    } else {
        if (this.history_state[this.Root_on_normal].indexOf(this.Root_on_normal_yellow) !== -1) {
            this.enter_Root_on_normal_yellow()
        }
        if (this.history_state[this.Root_on_normal].indexOf(this.Root_on_normal_green) !== -1) {
            this.enter_Root_on_normal_green()
        }
        if (this.history_state[this.Root_on_normal].indexOf(this.Root_on_normal_red) !== -1) {
            this.enter_Root_on_normal_red()
        }
    }
};

// Statechart transitions :

TrafficLight.prototype.transition_Root = function(event) {
    var catched = false;
    if (!catched) {
        if (this.current_state[this.Root][0] === this.Root_on) {
            catched = this.transition_Root_on(event);
        }
        else if (this.current_state[this.Root][0] === this.Root_off) {
            catched = this.transition_Root_off(event);
        }
    }
    return catched;
};

TrafficLight.prototype.transition_Root_on = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "stop_clicked" && event.port === "ui") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_on. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_on();
            this.enter_Root_off();
        }
        catched = true;
    }
    
    if (!catched) {
        if (this.current_state[this.Root_on][0] === this.Root_on_interrupted) {
            catched = this.transition_Root_on_interrupted(event);
        }
        else if (this.current_state[this.Root_on][0] === this.Root_on_normal) {
            catched = this.transition_Root_on_normal(event);
        }
    }
    return catched;
};

TrafficLight.prototype.transition_Root_on_interrupted = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "police_interrupt_clicked" && event.port === "ui") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_on_interrupted. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_on_interrupted();
            this.enter_Root_on_normal();
            this.enterHistoryShallow_Root_on_normal();
        }
        catched = true;
    }
    
    if (!catched) {
        if (this.current_state[this.Root_on_interrupted][0] === this.Root_on_interrupted_yellow) {
            catched = this.transition_Root_on_interrupted_yellow(event);
        }
        else if (this.current_state[this.Root_on_interrupted][0] === this.Root_on_interrupted_black) {
            catched = this.transition_Root_on_interrupted_black(event);
        }
    }
    return catched;
};

TrafficLight.prototype.transition_Root_on_interrupted_yellow = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "_0after") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_on_interrupted_yellow. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_on_interrupted_yellow();
            this.enter_Root_on_interrupted_black();
        }
        catched = true;
    }
    
    return catched;
};

TrafficLight.prototype.transition_Root_on_interrupted_black = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "_1after") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_on_interrupted_black. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_on_interrupted_black();
            this.enter_Root_on_interrupted_yellow();
        }
        catched = true;
    }
    
    return catched;
};

TrafficLight.prototype.transition_Root_on_normal = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "police_interrupt_clicked" && event.port === "ui") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_on_normal. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_on_normal();
            this.enterDefault_Root_on_interrupted();
        }
        catched = true;
    }
    
    if (!catched) {
        if (this.current_state[this.Root_on_normal][0] === this.Root_on_normal_yellow) {
            catched = this.transition_Root_on_normal_yellow(event);
        }
        else if (this.current_state[this.Root_on_normal][0] === this.Root_on_normal_green) {
            catched = this.transition_Root_on_normal_green(event);
        }
        else if (this.current_state[this.Root_on_normal][0] === this.Root_on_normal_red) {
            catched = this.transition_Root_on_normal_red(event);
        }
    }
    return catched;
};

TrafficLight.prototype.transition_Root_on_normal_yellow = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "_2after") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_on_normal_yellow. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_on_normal_yellow();
            this.enter_Root_on_normal_red();
        }
        catched = true;
    }
    
    return catched;
};

TrafficLight.prototype.transition_Root_on_normal_green = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "_3after") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_on_normal_green. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_on_normal_green();
            this.enter_Root_on_normal_yellow();
        }
        catched = true;
    }
    
    return catched;
};

TrafficLight.prototype.transition_Root_on_normal_red = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "_4after") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_on_normal_red. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_on_normal_red();
            this.enter_Root_on_normal_green();
        }
        catched = true;
    }
    
    return catched;
};

TrafficLight.prototype.transition_Root_off = function(event) {
    var catched = false;
    return catched;
};

// Execute transitions
TrafficLight.prototype.transition = function(event) {
    if (!event) event = new Event();
    this.state_changed = this.transition_Root(event);
};

// inState method for statechart
TrafficLight.prototype.inState = function(nodes) {
    for (var c in this.current_state) {
        if (!this.current_state.hasOwnProperty(c)) continue;
        var new_nodes = new Array();
        for (var n in nodes) {
            if (!nodes.hasOwnProperty(n)) continue;
            if (this.current_state[c].indexOf(nodes[n]) === -1) {
                new_nodes.push(nodes[n]);
            }
        }
        nodes = new_nodes;
        if (nodes.length === 0) {
            return true;
        }
    }
    return false;
};

TrafficLight.prototype.commonConstructor = function(controller) {
    if (!controller) controller = null;
    // Constructor part that is common for all constructors.
    RuntimeClassBase.call(this);
    
    // User defined input ports
    this.inports = new Object();
    this.controller = controller;
    this.object_manager = (controller == null ? null : controller.object_manager);
    this.current_state = new Object();
    this.history_state = new Object();
    this.timers = new Object();
    
    // Initialize statechart
    this.history_state[TrafficLight.Root_on_normal] = new Array();
    
    this.current_state[this.Root] = new Array();
    this.current_state[this.Root_on] = new Array();
    this.current_state[this.Root_on_interrupted] = new Array();
    this.current_state[this.Root_on_normal] = new Array();
};

TrafficLight.prototype.start = function() {
    RuntimeClassBase.prototype.start.call(this);
    this.enterDefault_Root_on();
};

// put class in global diagram object
Traffic_Light.TrafficLight = TrafficLight;

// The actual constructor
var MainApp = function(controller) {
    // Unique IDs for all statechart nodes
    this.Root = 0;
    this.Root_initializing = 1;
    this.Root_creating = 2;
    this.Root_initialized = 3;
    
    MainApp.prototype.commonConstructor.call(this,controller);
    
    // constructor body (user-defined)
    this.canvas = ui.append_canvas(ui.window, 100, 310, {'background':'#eee'});
    var police_button = ui.append_button(ui.window, 'Police interrupt');
    var stop_button = ui.append_button(ui.window, 'Stop');
    ui.bind_event(police_button.element, ui.EVENTS.MOUSE_CLICK, this.controller, 'police_interrupt_clicked');
    ui.bind_event(stop_button.element, ui.EVENTS.MOUSE_CLICK, this.controller, 'stop_clicked');
};


MainApp.prototype = new RuntimeClassBase();

// Statechart enter/exit action method(s) :

MainApp.prototype.enter_Root_initializing = function() {
    this.current_state[this.Root].push(this.Root_initializing);
};

MainApp.prototype.exit_Root_initializing = function() {
    this.current_state[this.Root] = new Array();
};

MainApp.prototype.enter_Root_creating = function() {
    this.current_state[this.Root].push(this.Root_creating);
};

MainApp.prototype.exit_Root_creating = function() {
    this.current_state[this.Root] = new Array();
};

MainApp.prototype.enter_Root_initialized = function() {
    this.current_state[this.Root].push(this.Root_initialized);
};

MainApp.prototype.exit_Root_initialized = function() {
    this.current_state[this.Root] = new Array();
};

// Statechart transitions :

MainApp.prototype.transition_Root = function(event) {
    var catched = false;
    if (!catched) {
        if (this.current_state[this.Root][0] === this.Root_initializing) {
            catched = this.transition_Root_initializing(event);
        }
        else if (this.current_state[this.Root][0] === this.Root_creating) {
            catched = this.transition_Root_creating(event);
        }
        else if (this.current_state[this.Root][0] === this.Root_initialized) {
            catched = this.transition_Root_initialized(event);
        }
    }
    return catched;
};

MainApp.prototype.transition_Root_initializing = function(event) {
    var catched = false;
    var enableds = new Array();
    enableds.push(1);
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_initializing. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_initializing();
            this.object_manager.addEvent(new Event("create_instance", null, [this, 'trafficlight','TrafficLight',this.canvas]));
            this.enter_Root_creating();
        }
        catched = true;
    }
    
    return catched;
};

MainApp.prototype.transition_Root_creating = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "instance_created") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_creating. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            var parameters = event.parameters;
            
            var association_name = parameters[0];
            this.exit_Root_creating();
            var send_event = new Event("set_association_name", null, [association_name]);
            this.object_manager.addEvent(new Event("narrow_cast", null, [this, association_name , send_event]));
            this.object_manager.addEvent(new Event("start_instance", null, [this, association_name]));
            this.enter_Root_initialized();
        }
        catched = true;
    }
    
    return catched;
};

MainApp.prototype.transition_Root_initialized = function(event) {
    var catched = false;
    return catched;
};

// Execute transitions
MainApp.prototype.transition = function(event) {
    if (!event) event = new Event();
    this.state_changed = this.transition_Root(event);
};

// inState method for statechart
MainApp.prototype.inState = function(nodes) {
    for (var c in this.current_state) {
        if (!this.current_state.hasOwnProperty(c)) continue;
        var new_nodes = new Array();
        for (var n in nodes) {
            if (!nodes.hasOwnProperty(n)) continue;
            if (this.current_state[c].indexOf(nodes[n]) === -1) {
                new_nodes.push(nodes[n]);
            }
        }
        nodes = new_nodes;
        if (nodes.length === 0) {
            return true;
        }
    }
    return false;
};

MainApp.prototype.commonConstructor = function(controller) {
    if (!controller) controller = null;
    // Constructor part that is common for all constructors.
    RuntimeClassBase.call(this);
    
    // User defined input ports
    this.inports = new Object();
    this.controller = controller;
    this.object_manager = (controller == null ? null : controller.object_manager);
    this.current_state = new Object();
    this.history_state = new Object();
    
    // Initialize statechart
    this.current_state[this.Root] = new Array();
};

MainApp.prototype.start = function() {
    RuntimeClassBase.prototype.start.call(this);
    this.enter_Root_initializing();
};

// put class in global diagram object
Traffic_Light.MainApp = MainApp;

var ObjectManager = function(controller) {
    ObjectManagerBase.call(this, controller);
};

ObjectManager.prototype = new ObjectManagerBase();

ObjectManager.prototype.instantiate = function(class_name, construct_params) {
    if (class_name === "TrafficLight") {
        var instance = new TrafficLight(this.controller, construct_params[0]);
        instance.associations = new Object();
    } else if (class_name === "MainApp") {
        var instance = new MainApp(this.controller);
        instance.associations = new Object();
        instance.associations["trafficlight"] = new Association("TrafficLight", 0, -1);
    }
    return instance;
};

// put in global diagram object
Traffic_Light.ObjectManager = ObjectManager;

var Controller = function(keep_running, finished_callback) {
    if (keep_running === undefined) keep_running = true;
    JsEventLoopControllerBase.call(this, new ObjectManager(this), keep_running, finished_callback);
    this.addInputPort("ui");
    this.object_manager.createInstance("MainApp", []);
};

Controller.prototype = new JsEventLoopControllerBase();

// put in global diagram object
Traffic_Light.Controller = Controller;

})();
