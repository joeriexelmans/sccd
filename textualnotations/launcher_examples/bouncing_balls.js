/**
 * Statechart compiler by Glenn De Jonghe
 * Javascript generator by Joeri Exelmans
 * 
 * Date:   Mon Aug 17 14:56:03 2015
 * 
 * Model author: Simon Van Mierlo+Joeri Exelmans+Raphael Mannadiar
 * Model name:   Bouncing_Balls
 * Model description:
    Tkinter frame with bouncing balls in it.
 */

// put everything in an object (serves as "namespace")
Bouncing_Balls = {};

// closure scope
(function() {

// The actual constructor
var Button = function(controller, parent, event_name, button_text) {
    // Unique IDs for all statechart nodes
    this.Root = 0;
    this.Root_initializing = 1;
    this.Root_running = 2;
    
    Button.prototype.commonConstructor.call(this,controller);
    
    // constructor body (user-defined)
    this.event_name = event_name;
    var button = ui.append_button(parent.field_window, event_name);
    ui.bind_event(button.element, ui.EVENTS.MOUSE_CLICK, this.controller, 'mouse_click');
};


Button.prototype = new RuntimeClassBase();

// Statechart enter/exit action method(s) :

Button.prototype.enter_Root_initializing = function() {
    this.current_state[this.Root].push(this.Root_initializing);
};

Button.prototype.exit_Root_initializing = function() {
    this.current_state[this.Root] = new Array();
};

Button.prototype.enter_Root_running = function() {
    this.current_state[this.Root].push(this.Root_running);
};

Button.prototype.exit_Root_running = function() {
    this.current_state[this.Root] = new Array();
};

// Statechart transitions :

Button.prototype.transition_Root = function(event) {
    var catched = false;
    if (!catched) {
        if (this.current_state[this.Root][0] === this.Root_initializing) {
            catched = this.transition_Root_initializing(event);
        }
        else if (this.current_state[this.Root][0] === this.Root_running) {
            catched = this.transition_Root_running(event);
        }
    }
    return catched;
};

Button.prototype.transition_Root_initializing = function(event) {
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
            var send_event = new Event("button_created", null, []);
            this.object_manager.addEvent(new Event("narrow_cast", null, [this, 'parent' , send_event]));
            this.enter_Root_running();
        }
        catched = true;
    }
    
    return catched;
};

Button.prototype.transition_Root_running = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "mouse_click" && event.port === "ui") {
        var parameters = event.parameters;
        
        var x = parameters[0];
        
        var y = parameters[1];
        
        var button = parameters[2];
        if (button == ui.MOUSE_BUTTONS.LEFT) {
            enableds.push(1);
        }
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_running. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            var parameters = event.parameters;
            
            var x = parameters[0];
            
            var y = parameters[1];
            
            var button = parameters[2];
            this.exit_Root_running();
            var send_event = new Event("button_pressed", null, [this.event_name]);
            this.object_manager.addEvent(new Event("narrow_cast", null, [this, 'parent' , send_event]));
            this.enter_Root_running();
        }
        catched = true;
    }
    
    return catched;
};

// Execute transitions
Button.prototype.transition = function(event) {
    if (!event) event = new Event();
    this.state_changed = this.transition_Root(event);
};

// inState method for statechart
Button.prototype.inState = function(nodes) {
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

Button.prototype.commonConstructor = function(controller) {
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

Button.prototype.start = function() {
    RuntimeClassBase.prototype.start.call(this);
    this.enter_Root_initializing();
};

// put class in global diagram object
Bouncing_Balls.Button = Button;

// The actual constructor
var Field = function(controller) {
    // Unique IDs for all statechart nodes
    this.Root = 0;
    this.Root_root = 1;
    this.Root_root_running = 2;
    this.Root_root_running_main_behaviour = 3;
    this.Root_root_running_deleting_behaviour = 4;
    this.Root_root_running_child_behaviour = 5;
    this.Root_root_waiting = 6;
    this.Root_root_packing = 7;
    this.Root_root_deleting = 8;
    this.Root_root_creating = 9;
    this.Root_root_initializing = 10;
    this.Root_root_deleted = 11;
    this.Root_root_running_main_behaviour_running = 12;
    this.Root_root_running_main_behaviour_creating = 13;
    this.Root_root_running_deleting_behaviour_running = 14;
    this.Root_root_running_child_behaviour_listening = 15;
    
    Field.prototype.commonConstructor.call(this,controller);
    
    // constructor body (user-defined)
    this.field_window = ui.new_window(400, 450);
    this.canvas = ui.append_canvas(this.field_window, 400, 400, {'background':'#eee'});
    ui.bind_event(this.field_window, ui.EVENTS.WINDOW_CLOSE, this.controller, 'window_close');
    ui.bind_event(this.field_window, ui.EVENTS.KEY_PRESS, this.controller, 'key_press');
    ui.bind_event(this.canvas.element, ui.EVENTS.MOUSE_RIGHT_CLICK, this.controller, 'right_click', this.inports['field_ui']);
    ui.bind_event(this.canvas.element, ui.EVENTS.MOUSE_MOVE, this.controller, 'mouse_move');
    ui.bind_event(this.canvas.element, ui.EVENTS.MOUSE_RELEASE, this.controller, 'mouse_release');
};


Field.prototype = new RuntimeClassBase();

// User defined destructor
Field.prototype.destructor = function() {
    ui.close_window(this.field_window);
    
};
// Statechart enter/exit action method(s) :

Field.prototype.enter_Root_root = function() {
    this.current_state[this.Root].push(this.Root_root);
};

Field.prototype.exit_Root_root = function() {
    if (this.current_state[this.Root_root].indexOf(this.Root_root_waiting) !== -1) {
        this.exit_Root_root_waiting();
    }
    if (this.current_state[this.Root_root].indexOf(this.Root_root_packing) !== -1) {
        this.exit_Root_root_packing();
    }
    if (this.current_state[this.Root_root].indexOf(this.Root_root_deleting) !== -1) {
        this.exit_Root_root_deleting();
    }
    if (this.current_state[this.Root_root].indexOf(this.Root_root_creating) !== -1) {
        this.exit_Root_root_creating();
    }
    if (this.current_state[this.Root_root].indexOf(this.Root_root_initializing) !== -1) {
        this.exit_Root_root_initializing();
    }
    if (this.current_state[this.Root_root].indexOf(this.Root_root_deleted) !== -1) {
        this.exit_Root_root_deleted();
    }
    if (this.current_state[this.Root_root].indexOf(this.Root_root_running) !== -1) {
        this.exit_Root_root_running();
    }
    this.current_state[this.Root] = new Array();
};

Field.prototype.enter_Root_root_running = function() {
    this.current_state[this.Root_root].push(this.Root_root_running);
};

Field.prototype.exit_Root_root_running = function() {
    this.exit_Root_root_running_main_behaviour();
    this.exit_Root_root_running_deleting_behaviour();
    this.exit_Root_root_running_child_behaviour();
    this.current_state[this.Root_root] = new Array();
};

Field.prototype.enter_Root_root_running_main_behaviour = function() {
    this.current_state[this.Root_root_running].push(this.Root_root_running_main_behaviour);
};

Field.prototype.exit_Root_root_running_main_behaviour = function() {
    if (this.current_state[this.Root_root_running_main_behaviour].indexOf(this.Root_root_running_main_behaviour_running) !== -1) {
        this.exit_Root_root_running_main_behaviour_running();
    }
    if (this.current_state[this.Root_root_running_main_behaviour].indexOf(this.Root_root_running_main_behaviour_creating) !== -1) {
        this.exit_Root_root_running_main_behaviour_creating();
    }
    this.current_state[this.Root_root_running] = new Array();
};

Field.prototype.enter_Root_root_running_deleting_behaviour = function() {
    this.current_state[this.Root_root_running].push(this.Root_root_running_deleting_behaviour);
};

Field.prototype.exit_Root_root_running_deleting_behaviour = function() {
    if (this.current_state[this.Root_root_running_deleting_behaviour].indexOf(this.Root_root_running_deleting_behaviour_running) !== -1) {
        this.exit_Root_root_running_deleting_behaviour_running();
    }
    this.current_state[this.Root_root_running] = new Array();
};

Field.prototype.enter_Root_root_running_child_behaviour = function() {
    this.current_state[this.Root_root_running].push(this.Root_root_running_child_behaviour);
};

Field.prototype.exit_Root_root_running_child_behaviour = function() {
    if (this.current_state[this.Root_root_running_child_behaviour].indexOf(this.Root_root_running_child_behaviour_listening) !== -1) {
        this.exit_Root_root_running_child_behaviour_listening();
    }
    this.current_state[this.Root_root_running] = new Array();
};

Field.prototype.enter_Root_root_waiting = function() {
    this.current_state[this.Root_root].push(this.Root_root_waiting);
};

Field.prototype.exit_Root_root_waiting = function() {
    this.current_state[this.Root_root] = new Array();
};

Field.prototype.enter_Root_root_packing = function() {
    this.current_state[this.Root_root].push(this.Root_root_packing);
};

Field.prototype.exit_Root_root_packing = function() {
    this.current_state[this.Root_root] = new Array();
};

Field.prototype.enter_Root_root_deleting = function() {
    this.timers[0] = 0.05 * 1000.0; /* convert ms to s */
    this.current_state[this.Root_root].push(this.Root_root_deleting);
};

Field.prototype.exit_Root_root_deleting = function() {
    delete this.timers[0];
    this.current_state[this.Root_root] = new Array();
};

Field.prototype.enter_Root_root_creating = function() {
    this.current_state[this.Root_root].push(this.Root_root_creating);
};

Field.prototype.exit_Root_root_creating = function() {
    this.current_state[this.Root_root] = new Array();
};

Field.prototype.enter_Root_root_initializing = function() {
    this.current_state[this.Root_root].push(this.Root_root_initializing);
};

Field.prototype.exit_Root_root_initializing = function() {
    this.current_state[this.Root_root] = new Array();
};

Field.prototype.enter_Root_root_deleted = function() {
    this.current_state[this.Root_root].push(this.Root_root_deleted);
};

Field.prototype.exit_Root_root_deleted = function() {
    this.current_state[this.Root_root] = new Array();
};

Field.prototype.enter_Root_root_running_main_behaviour_running = function() {
    this.current_state[this.Root_root_running_main_behaviour].push(this.Root_root_running_main_behaviour_running);
};

Field.prototype.exit_Root_root_running_main_behaviour_running = function() {
    this.current_state[this.Root_root_running_main_behaviour] = new Array();
};

Field.prototype.enter_Root_root_running_main_behaviour_creating = function() {
    this.current_state[this.Root_root_running_main_behaviour].push(this.Root_root_running_main_behaviour_creating);
};

Field.prototype.exit_Root_root_running_main_behaviour_creating = function() {
    this.current_state[this.Root_root_running_main_behaviour] = new Array();
};

Field.prototype.enter_Root_root_running_deleting_behaviour_running = function() {
    this.current_state[this.Root_root_running_deleting_behaviour].push(this.Root_root_running_deleting_behaviour_running);
};

Field.prototype.exit_Root_root_running_deleting_behaviour_running = function() {
    this.current_state[this.Root_root_running_deleting_behaviour] = new Array();
};

Field.prototype.enter_Root_root_running_child_behaviour_listening = function() {
    this.current_state[this.Root_root_running_child_behaviour].push(this.Root_root_running_child_behaviour_listening);
};

Field.prototype.exit_Root_root_running_child_behaviour_listening = function() {
    this.current_state[this.Root_root_running_child_behaviour] = new Array();
};

// Statechart enter/exit default method(s) :

Field.prototype.enterDefault_Root_root = function() {
    this.enter_Root_root();
    this.enter_Root_root_waiting();
};

Field.prototype.enterDefault_Root_root_running = function() {
    this.enter_Root_root_running();
    this.enterDefault_Root_root_running_main_behaviour();
    this.enterDefault_Root_root_running_deleting_behaviour();
    this.enterDefault_Root_root_running_child_behaviour();
};

Field.prototype.enterDefault_Root_root_running_main_behaviour = function() {
    this.enter_Root_root_running_main_behaviour();
    this.enter_Root_root_running_main_behaviour_running();
};

Field.prototype.enterDefault_Root_root_running_deleting_behaviour = function() {
    this.enter_Root_root_running_deleting_behaviour();
    this.enter_Root_root_running_deleting_behaviour_running();
};

Field.prototype.enterDefault_Root_root_running_child_behaviour = function() {
    this.enter_Root_root_running_child_behaviour();
    this.enter_Root_root_running_child_behaviour_listening();
};

// Statechart transitions :

Field.prototype.transition_Root = function(event) {
    var catched = false;
    if (!catched) {
        if (this.current_state[this.Root][0] === this.Root_root) {
            catched = this.transition_Root_root(event);
        }
    }
    return catched;
};

Field.prototype.transition_Root_root = function(event) {
    var catched = false;
    if (!catched) {
        if (this.current_state[this.Root_root][0] === this.Root_root_waiting) {
            catched = this.transition_Root_root_waiting(event);
        }
        else if (this.current_state[this.Root_root][0] === this.Root_root_packing) {
            catched = this.transition_Root_root_packing(event);
        }
        else if (this.current_state[this.Root_root][0] === this.Root_root_deleting) {
            catched = this.transition_Root_root_deleting(event);
        }
        else if (this.current_state[this.Root_root][0] === this.Root_root_creating) {
            catched = this.transition_Root_root_creating(event);
        }
        else if (this.current_state[this.Root_root][0] === this.Root_root_initializing) {
            catched = this.transition_Root_root_initializing(event);
        }
        else if (this.current_state[this.Root_root][0] === this.Root_root_deleted) {
            catched = this.transition_Root_root_deleted(event);
        }
        else if (this.current_state[this.Root_root][0] === this.Root_root_running) {
            catched = this.transition_Root_root_running(event);
        }
    }
    return catched;
};

Field.prototype.transition_Root_root_waiting = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "set_association_name") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_root_waiting. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            var parameters = event.parameters;
            
            var association_name = parameters[0];
            this.exit_Root_root_waiting();
            this.association_name = association_name;
            this.enter_Root_root_initializing();
        }
        catched = true;
    }
    
    return catched;
};

Field.prototype.transition_Root_root_packing = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "button_created") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_root_packing. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_root_packing();
            this.enterDefault_Root_root_running();
        }
        catched = true;
    }
    
    return catched;
};

Field.prototype.transition_Root_root_deleting = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "_0after") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_root_deleting. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_root_deleting();
            var send_event = new Event("delete_field", null, [this.association_name]);
            this.object_manager.addEvent(new Event("narrow_cast", null, [this, 'parent' , send_event]));
            this.enter_Root_root_deleted();
        }
        catched = true;
    }
    
    return catched;
};

Field.prototype.transition_Root_root_creating = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "instance_created") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_root_creating. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            var parameters = event.parameters;
            
            var association_name = parameters[0];
            this.exit_Root_root_creating();
            this.object_manager.addEvent(new Event("start_instance", null, [this, association_name]));
            this.enter_Root_root_packing();
        }
        catched = true;
    }
    
    return catched;
};

Field.prototype.transition_Root_root_initializing = function(event) {
    var catched = false;
    var enableds = new Array();
    enableds.push(1);
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_root_initializing. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_root_initializing();
            this.object_manager.addEvent(new Event("create_instance", null, [this, 'buttons','Button',this,'create_new_field','Spawn New Window']));
            this.enter_Root_root_creating();
        }
        catched = true;
    }
    
    return catched;
};

Field.prototype.transition_Root_root_deleted = function(event) {
    var catched = false;
    return catched;
};

Field.prototype.transition_Root_root_running = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "window_close" && event.port === "ui") {
        var parameters = event.parameters;
        
        var window = parameters[0];
        if (window == this.field_window || window == ui.window) {
            enableds.push(1);
        }
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_root_running. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            var parameters = event.parameters;
            
            var window = parameters[0];
            this.exit_Root_root_running();
            this.object_manager.addEvent(new Event("delete_instance", null, [this, 'buttons']));
            var send_event = new Event("delete_self", null, []);
            this.object_manager.addEvent(new Event("narrow_cast", null, [this, 'balls' , send_event]));
            this.enter_Root_root_deleting();
        }
        catched = true;
    }
    
    if (!catched) {
        catched = this.transition_Root_root_running_main_behaviour(event) || catched
        catched = this.transition_Root_root_running_deleting_behaviour(event) || catched
        catched = this.transition_Root_root_running_child_behaviour(event) || catched
    }
    return catched;
};

Field.prototype.transition_Root_root_running_main_behaviour = function(event) {
    var catched = false;
    if (!catched) {
        if (this.current_state[this.Root_root_running_main_behaviour][0] === this.Root_root_running_main_behaviour_running) {
            catched = this.transition_Root_root_running_main_behaviour_running(event);
        }
        else if (this.current_state[this.Root_root_running_main_behaviour][0] === this.Root_root_running_main_behaviour_creating) {
            catched = this.transition_Root_root_running_main_behaviour_creating(event);
        }
    }
    return catched;
};

Field.prototype.transition_Root_root_running_main_behaviour_running = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "right_click" && event.port === "field_ui") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_root_running_main_behaviour_running. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            var parameters = event.parameters;
            
            var x = parameters[0];
            
            var y = parameters[1];
            
            var button = parameters[2];
            this.exit_Root_root_running_main_behaviour_running();
            this.object_manager.addEvent(new Event("create_instance", null, [this, 'balls','Ball',this.canvas,x,y,this.field_window]));
            this.enter_Root_root_running_main_behaviour_creating();
        }
        catched = true;
    }
    
    return catched;
};

Field.prototype.transition_Root_root_running_main_behaviour_creating = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "instance_created") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_root_running_main_behaviour_creating. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            var parameters = event.parameters;
            
            var association_name = parameters[0];
            this.exit_Root_root_running_main_behaviour_creating();
            var send_event = new Event("set_association_name", null, [association_name]);
            this.object_manager.addEvent(new Event("narrow_cast", null, [this, association_name , send_event]));
            this.object_manager.addEvent(new Event("start_instance", null, [this, association_name]));
            this.enter_Root_root_running_main_behaviour_running();
        }
        catched = true;
    }
    
    return catched;
};

Field.prototype.transition_Root_root_running_deleting_behaviour = function(event) {
    var catched = false;
    if (!catched) {
        if (this.current_state[this.Root_root_running_deleting_behaviour][0] === this.Root_root_running_deleting_behaviour_running) {
            catched = this.transition_Root_root_running_deleting_behaviour_running(event);
        }
    }
    return catched;
};

Field.prototype.transition_Root_root_running_deleting_behaviour_running = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "delete_ball") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_root_running_deleting_behaviour_running. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            var parameters = event.parameters;
            
            var association_name = parameters[0];
            this.exit_Root_root_running_deleting_behaviour_running();
            this.object_manager.addEvent(new Event("delete_instance", null, [this, association_name]));
            this.enter_Root_root_running_deleting_behaviour_running();
        }
        catched = true;
    }
    
    return catched;
};

Field.prototype.transition_Root_root_running_child_behaviour = function(event) {
    var catched = false;
    if (!catched) {
        if (this.current_state[this.Root_root_running_child_behaviour][0] === this.Root_root_running_child_behaviour_listening) {
            catched = this.transition_Root_root_running_child_behaviour_listening(event);
        }
    }
    return catched;
};

Field.prototype.transition_Root_root_running_child_behaviour_listening = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "button_pressed") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_root_running_child_behaviour_listening. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            var parameters = event.parameters;
            
            var event_name = parameters[0];
            this.exit_Root_root_running_child_behaviour_listening();
            var send_event = new Event("button_pressed", null, [event_name]);
            this.object_manager.addEvent(new Event("narrow_cast", null, [this, 'parent' , send_event]));
            this.enter_Root_root_running_child_behaviour_listening();
        }
        catched = true;
    }
    
    return catched;
};

// Execute transitions
Field.prototype.transition = function(event) {
    if (!event) event = new Event();
    this.state_changed = this.transition_Root(event);
};

// inState method for statechart
Field.prototype.inState = function(nodes) {
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

Field.prototype.commonConstructor = function(controller) {
    if (!controller) controller = null;
    // Constructor part that is common for all constructors.
    RuntimeClassBase.call(this);
    
    // User defined input ports
    this.inports = new Object();
    this.inports["field_ui"] = controller.addInputPort("field_ui", this);
    
    // User defined attributes
    this.field_window = null;
    this.canvas = null;
    
    this.controller = controller;
    this.object_manager = (controller == null ? null : controller.object_manager);
    this.current_state = new Object();
    this.history_state = new Object();
    this.timers = new Object();
    
    // Initialize statechart
    this.current_state[this.Root] = new Array();
    this.current_state[this.Root_root] = new Array();
    this.current_state[this.Root_root_running] = new Array();
    this.current_state[this.Root_root_running_main_behaviour] = new Array();
    this.current_state[this.Root_root_running_deleting_behaviour] = new Array();
    this.current_state[this.Root_root_running_child_behaviour] = new Array();
};

Field.prototype.start = function() {
    RuntimeClassBase.prototype.start.call(this);
    this.enterDefault_Root_root();
};

// put class in global diagram object
Bouncing_Balls.Field = Field;

// The actual constructor
var MainApp = function(controller) {
    // Unique IDs for all statechart nodes
    this.Root = 0;
    this.Root_running = 1;
    this.Root_running_root = 2;
    this.Root_running_root_main_behaviour = 3;
    this.Root_running_root_cd_behaviour = 4;
    this.Root_running_stopped = 5;
    this.Root_running_root_main_behaviour_initializing = 6;
    this.Root_running_root_main_behaviour_running = 7;
    this.Root_running_root_cd_behaviour_creating = 8;
    this.Root_running_root_cd_behaviour_waiting = 9;
    this.Root_running_root_cd_behaviour_check_nr_of_fields = 10;
    
    MainApp.prototype.commonConstructor.call(this,controller);
    
    // constructor body (user-defined)
    this.nr_of_fields = 0;
    ui.bind_event(ui.window, ui.EVENTS.WINDOW_CLOSE, this.controller, 'window_close');
};


MainApp.prototype = new RuntimeClassBase();

// Statechart enter/exit action method(s) :

MainApp.prototype.enter_Root_running = function() {
    this.current_state[this.Root].push(this.Root_running);
};

MainApp.prototype.exit_Root_running = function() {
    if (this.current_state[this.Root_running].indexOf(this.Root_running_stopped) !== -1) {
        this.exit_Root_running_stopped();
    }
    if (this.current_state[this.Root_running].indexOf(this.Root_running_root) !== -1) {
        this.exit_Root_running_root();
    }
    this.current_state[this.Root] = new Array();
};

MainApp.prototype.enter_Root_running_root = function() {
    this.current_state[this.Root_running].push(this.Root_running_root);
};

MainApp.prototype.exit_Root_running_root = function() {
    this.exit_Root_running_root_main_behaviour();
    this.exit_Root_running_root_cd_behaviour();
    this.current_state[this.Root_running] = new Array();
};

MainApp.prototype.enter_Root_running_root_main_behaviour = function() {
    this.current_state[this.Root_running_root].push(this.Root_running_root_main_behaviour);
};

MainApp.prototype.exit_Root_running_root_main_behaviour = function() {
    if (this.current_state[this.Root_running_root_main_behaviour].indexOf(this.Root_running_root_main_behaviour_initializing) !== -1) {
        this.exit_Root_running_root_main_behaviour_initializing();
    }
    if (this.current_state[this.Root_running_root_main_behaviour].indexOf(this.Root_running_root_main_behaviour_running) !== -1) {
        this.exit_Root_running_root_main_behaviour_running();
    }
    this.current_state[this.Root_running_root] = new Array();
};

MainApp.prototype.enter_Root_running_root_cd_behaviour = function() {
    this.current_state[this.Root_running_root].push(this.Root_running_root_cd_behaviour);
};

MainApp.prototype.exit_Root_running_root_cd_behaviour = function() {
    if (this.current_state[this.Root_running_root_cd_behaviour].indexOf(this.Root_running_root_cd_behaviour_creating) !== -1) {
        this.exit_Root_running_root_cd_behaviour_creating();
    }
    if (this.current_state[this.Root_running_root_cd_behaviour].indexOf(this.Root_running_root_cd_behaviour_waiting) !== -1) {
        this.exit_Root_running_root_cd_behaviour_waiting();
    }
    if (this.current_state[this.Root_running_root_cd_behaviour].indexOf(this.Root_running_root_cd_behaviour_check_nr_of_fields) !== -1) {
        this.exit_Root_running_root_cd_behaviour_check_nr_of_fields();
    }
    this.current_state[this.Root_running_root] = new Array();
};

MainApp.prototype.enter_Root_running_stopped = function() {
    this.current_state[this.Root_running].push(this.Root_running_stopped);
};

MainApp.prototype.exit_Root_running_stopped = function() {
    this.current_state[this.Root_running] = new Array();
};

MainApp.prototype.enter_Root_running_root_main_behaviour_initializing = function() {
    this.current_state[this.Root_running_root_main_behaviour].push(this.Root_running_root_main_behaviour_initializing);
};

MainApp.prototype.exit_Root_running_root_main_behaviour_initializing = function() {
    this.current_state[this.Root_running_root_main_behaviour] = new Array();
};

MainApp.prototype.enter_Root_running_root_main_behaviour_running = function() {
    this.current_state[this.Root_running_root_main_behaviour].push(this.Root_running_root_main_behaviour_running);
};

MainApp.prototype.exit_Root_running_root_main_behaviour_running = function() {
    this.current_state[this.Root_running_root_main_behaviour] = new Array();
};

MainApp.prototype.enter_Root_running_root_cd_behaviour_creating = function() {
    this.current_state[this.Root_running_root_cd_behaviour].push(this.Root_running_root_cd_behaviour_creating);
};

MainApp.prototype.exit_Root_running_root_cd_behaviour_creating = function() {
    this.current_state[this.Root_running_root_cd_behaviour] = new Array();
};

MainApp.prototype.enter_Root_running_root_cd_behaviour_waiting = function() {
    this.current_state[this.Root_running_root_cd_behaviour].push(this.Root_running_root_cd_behaviour_waiting);
};

MainApp.prototype.exit_Root_running_root_cd_behaviour_waiting = function() {
    this.current_state[this.Root_running_root_cd_behaviour] = new Array();
};

MainApp.prototype.enter_Root_running_root_cd_behaviour_check_nr_of_fields = function() {
    this.current_state[this.Root_running_root_cd_behaviour].push(this.Root_running_root_cd_behaviour_check_nr_of_fields);
};

MainApp.prototype.exit_Root_running_root_cd_behaviour_check_nr_of_fields = function() {
    this.current_state[this.Root_running_root_cd_behaviour] = new Array();
};

// Statechart enter/exit default method(s) :

MainApp.prototype.enterDefault_Root_running = function() {
    this.enter_Root_running();
    this.enterDefault_Root_running_root();
};

MainApp.prototype.enterDefault_Root_running_root = function() {
    this.enter_Root_running_root();
    this.enterDefault_Root_running_root_main_behaviour();
    this.enterDefault_Root_running_root_cd_behaviour();
};

MainApp.prototype.enterDefault_Root_running_root_main_behaviour = function() {
    this.enter_Root_running_root_main_behaviour();
    this.enter_Root_running_root_main_behaviour_initializing();
};

MainApp.prototype.enterDefault_Root_running_root_cd_behaviour = function() {
    this.enter_Root_running_root_cd_behaviour();
    this.enter_Root_running_root_cd_behaviour_waiting();
};

// Statechart transitions :

MainApp.prototype.transition_Root = function(event) {
    var catched = false;
    if (!catched) {
        if (this.current_state[this.Root][0] === this.Root_running) {
            catched = this.transition_Root_running(event);
        }
    }
    return catched;
};

MainApp.prototype.transition_Root_running = function(event) {
    var catched = false;
    if (!catched) {
        if (this.current_state[this.Root_running][0] === this.Root_running_stopped) {
            catched = this.transition_Root_running_stopped(event);
        }
        else if (this.current_state[this.Root_running][0] === this.Root_running_root) {
            catched = this.transition_Root_running_root(event);
        }
    }
    return catched;
};

MainApp.prototype.transition_Root_running_stopped = function(event) {
    var catched = false;
    return catched;
};

MainApp.prototype.transition_Root_running_root = function(event) {
    var catched = false;
    if (!catched) {
        catched = this.transition_Root_running_root_main_behaviour(event) || catched
        catched = this.transition_Root_running_root_cd_behaviour(event) || catched
    }
    return catched;
};

MainApp.prototype.transition_Root_running_root_main_behaviour = function(event) {
    var catched = false;
    if (!catched) {
        if (this.current_state[this.Root_running_root_main_behaviour][0] === this.Root_running_root_main_behaviour_initializing) {
            catched = this.transition_Root_running_root_main_behaviour_initializing(event);
        }
        else if (this.current_state[this.Root_running_root_main_behaviour][0] === this.Root_running_root_main_behaviour_running) {
            catched = this.transition_Root_running_root_main_behaviour_running(event);
        }
    }
    return catched;
};

MainApp.prototype.transition_Root_running_root_main_behaviour_initializing = function(event) {
    var catched = false;
    var enableds = new Array();
    enableds.push(1);
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_running_root_main_behaviour_initializing. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_running_root_main_behaviour_initializing();
            this.addEvent(new Event("create_field", null, []));
            this.enter_Root_running_root_main_behaviour_running();
        }
        catched = true;
    }
    
    return catched;
};

MainApp.prototype.transition_Root_running_root_main_behaviour_running = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "button_pressed") {
        var parameters = event.parameters;
        
        var event_name = parameters[0];
        if (event_name == 'create_new_field') {
            enableds.push(1);
        }
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_running_root_main_behaviour_running. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            var parameters = event.parameters;
            
            var event_name = parameters[0];
            this.exit_Root_running_root_main_behaviour_running();
            this.addEvent(new Event("create_field", null, []));
            this.enter_Root_running_root_main_behaviour_running();
        }
        catched = true;
    }
    
    return catched;
};

MainApp.prototype.transition_Root_running_root_cd_behaviour = function(event) {
    var catched = false;
    if (!catched) {
        if (this.current_state[this.Root_running_root_cd_behaviour][0] === this.Root_running_root_cd_behaviour_creating) {
            catched = this.transition_Root_running_root_cd_behaviour_creating(event);
        }
        else if (this.current_state[this.Root_running_root_cd_behaviour][0] === this.Root_running_root_cd_behaviour_waiting) {
            catched = this.transition_Root_running_root_cd_behaviour_waiting(event);
        }
        else if (this.current_state[this.Root_running_root_cd_behaviour][0] === this.Root_running_root_cd_behaviour_check_nr_of_fields) {
            catched = this.transition_Root_running_root_cd_behaviour_check_nr_of_fields(event);
        }
    }
    return catched;
};

MainApp.prototype.transition_Root_running_root_cd_behaviour_creating = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "instance_created") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_running_root_cd_behaviour_creating. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            var parameters = event.parameters;
            
            var association_name = parameters[0];
            this.exit_Root_running_root_cd_behaviour_creating();
            this.object_manager.addEvent(new Event("start_instance", null, [this, association_name]));
            var send_event = new Event("set_association_name", null, [association_name]);
            this.object_manager.addEvent(new Event("narrow_cast", null, [this, association_name , send_event]));
            this.nr_of_fields += 1;
            this.enter_Root_running_root_cd_behaviour_waiting();
        }
        catched = true;
    }
    
    return catched;
};

MainApp.prototype.transition_Root_running_root_cd_behaviour_waiting = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "create_field") {
        enableds.push(1);
    }
    
    if (event.name === "delete_field") {
        enableds.push(2);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_running_root_cd_behaviour_waiting. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_running_root_cd_behaviour_waiting();
            this.object_manager.addEvent(new Event("create_instance", null, [this, 'fields']));
            this.enter_Root_running_root_cd_behaviour_creating();
        }
        else if (enabled === 2) {
            var parameters = event.parameters;
            
            var association_name = parameters[0];
            this.exit_Root_running_root_cd_behaviour_waiting();
            this.object_manager.addEvent(new Event("delete_instance", null, [this, association_name]));
            this.nr_of_fields -= 1;
            this.enter_Root_running_root_cd_behaviour_check_nr_of_fields();
        }
        catched = true;
    }
    
    return catched;
};

MainApp.prototype.transition_Root_running_root_cd_behaviour_check_nr_of_fields = function(event) {
    var catched = false;
    var enableds = new Array();
    if (this.nr_of_fields != 0) {
        enableds.push(1);
    }
    
    if (this.nr_of_fields == 0) {
        enableds.push(2);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_running_root_cd_behaviour_check_nr_of_fields. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_running_root_cd_behaviour_check_nr_of_fields();
            this.enter_Root_running_root_cd_behaviour_waiting();
        }
        else if (enabled === 2) {
            this.exit_Root_running_root();
            ui.close_window(ui.window);
            this.enter_Root_running_stopped();
        }
        catched = true;
    }
    
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
    this.current_state[this.Root_running] = new Array();
    this.current_state[this.Root_running_root] = new Array();
    this.current_state[this.Root_running_root_main_behaviour] = new Array();
    this.current_state[this.Root_running_root_cd_behaviour] = new Array();
};

MainApp.prototype.start = function() {
    RuntimeClassBase.prototype.start.call(this);
    this.enterDefault_Root_running();
};

// put class in global diagram object
Bouncing_Balls.MainApp = MainApp;

// The actual constructor
var Ball = function(controller, canvas, x, y, field_window) {
    // Unique IDs for all statechart nodes
    this.Root = 0;
    this.Root_main_behaviour = 1;
    this.Root_main_behaviour_dragging = 2;
    this.Root_main_behaviour_selected = 3;
    this.Root_main_behaviour_initializing = 4;
    this.Root_main_behaviour_bouncing = 5;
    this.Root_deleted = 6;
    
    Ball.prototype.commonConstructor.call(this,controller);
    
    // constructor body (user-defined)
    this.canvas = canvas;
    this.field_window = field_window;
    this.r = 20.0;
    this.vel = {'x':utils.random() * 2.0 - 1.0, 'y':utils.random() * 2.0 - 1.0};
    this.mouse_pos = {'':''};
    this.smooth = 0.4;
    var circle = this.canvas.add_circle(x, y, this.r, {'fill':'#000'});
    ui.bind_event(circle, ui.EVENTS.MOUSE_PRESS, this.controller, 'mouse_press', this.inports['ball_ui']);
    ui.bind_event(circle, ui.EVENTS.MOUSE_RIGHT_CLICK, this.controller, 'right_click');
    this.element = circle;
};


Ball.prototype = new RuntimeClassBase();

// User defined destructor
Ball.prototype.destructor = function() {
    this.canvas.remove_element(this.element);
    
};
// Statechart enter/exit action method(s) :

Ball.prototype.enter_Root_main_behaviour = function() {
    this.current_state[this.Root].push(this.Root_main_behaviour);
};

Ball.prototype.exit_Root_main_behaviour = function() {
    if (this.current_state[this.Root_main_behaviour].indexOf(this.Root_main_behaviour_dragging) !== -1) {
        this.exit_Root_main_behaviour_dragging();
    }
    if (this.current_state[this.Root_main_behaviour].indexOf(this.Root_main_behaviour_selected) !== -1) {
        this.exit_Root_main_behaviour_selected();
    }
    if (this.current_state[this.Root_main_behaviour].indexOf(this.Root_main_behaviour_initializing) !== -1) {
        this.exit_Root_main_behaviour_initializing();
    }
    if (this.current_state[this.Root_main_behaviour].indexOf(this.Root_main_behaviour_bouncing) !== -1) {
        this.exit_Root_main_behaviour_bouncing();
    }
    this.current_state[this.Root] = new Array();
};

Ball.prototype.enter_Root_main_behaviour_dragging = function() {
    this.current_state[this.Root_main_behaviour].push(this.Root_main_behaviour_dragging);
};

Ball.prototype.exit_Root_main_behaviour_dragging = function() {
    this.current_state[this.Root_main_behaviour] = new Array();
};

Ball.prototype.enter_Root_main_behaviour_selected = function() {
    this.current_state[this.Root_main_behaviour].push(this.Root_main_behaviour_selected);
};

Ball.prototype.exit_Root_main_behaviour_selected = function() {
    this.current_state[this.Root_main_behaviour] = new Array();
};

Ball.prototype.enter_Root_main_behaviour_initializing = function() {
    this.current_state[this.Root_main_behaviour].push(this.Root_main_behaviour_initializing);
};

Ball.prototype.exit_Root_main_behaviour_initializing = function() {
    this.current_state[this.Root_main_behaviour] = new Array();
};

Ball.prototype.enter_Root_main_behaviour_bouncing = function() {
    this.timers[0] = 0.01 * 1000.0; /* convert ms to s */
    this.current_state[this.Root_main_behaviour].push(this.Root_main_behaviour_bouncing);
};

Ball.prototype.exit_Root_main_behaviour_bouncing = function() {
    delete this.timers[0];
    this.current_state[this.Root_main_behaviour] = new Array();
};

Ball.prototype.enter_Root_deleted = function() {
    this.current_state[this.Root].push(this.Root_deleted);
};

Ball.prototype.exit_Root_deleted = function() {
    this.current_state[this.Root] = new Array();
};

// Statechart enter/exit default method(s) :

Ball.prototype.enterDefault_Root_main_behaviour = function() {
    this.enter_Root_main_behaviour();
    this.enter_Root_main_behaviour_initializing();
};

// Statechart transitions :

Ball.prototype.transition_Root = function(event) {
    var catched = false;
    if (!catched) {
        if (this.current_state[this.Root][0] === this.Root_main_behaviour) {
            catched = this.transition_Root_main_behaviour(event);
        }
        else if (this.current_state[this.Root][0] === this.Root_deleted) {
            catched = this.transition_Root_deleted(event);
        }
    }
    return catched;
};

Ball.prototype.transition_Root_main_behaviour = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "delete_self") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_main_behaviour. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_main_behaviour();
            var send_event = new Event("delete_ball", null, [this.association_name]);
            this.object_manager.addEvent(new Event("narrow_cast", null, [this, 'parent' , send_event]));
            this.enter_Root_deleted();
        }
        catched = true;
    }
    
    if (!catched) {
        if (this.current_state[this.Root_main_behaviour][0] === this.Root_main_behaviour_dragging) {
            catched = this.transition_Root_main_behaviour_dragging(event);
        }
        else if (this.current_state[this.Root_main_behaviour][0] === this.Root_main_behaviour_selected) {
            catched = this.transition_Root_main_behaviour_selected(event);
        }
        else if (this.current_state[this.Root_main_behaviour][0] === this.Root_main_behaviour_initializing) {
            catched = this.transition_Root_main_behaviour_initializing(event);
        }
        else if (this.current_state[this.Root_main_behaviour][0] === this.Root_main_behaviour_bouncing) {
            catched = this.transition_Root_main_behaviour_bouncing(event);
        }
    }
    return catched;
};

Ball.prototype.transition_Root_main_behaviour_dragging = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "mouse_release" && event.port === "ui") {
        enableds.push(1);
    }
    
    if (event.name === "mouse_move" && event.port === "ui") {
        enableds.push(2);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_main_behaviour_dragging. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            var parameters = event.parameters;
            
            var x = parameters[0];
            
            var y = parameters[1];
            this.exit_Root_main_behaviour_dragging();
            this.element.set_color('#f00');
            this.enter_Root_main_behaviour_bouncing();
        }
        else if (enabled === 2) {
            var parameters = event.parameters;
            
            var x = parameters[0];
            
            var y = parameters[1];
            
            var button = parameters[2];
            this.exit_Root_main_behaviour_dragging();
            var dx = x - this.mouse_pos['x'];
            var dy = y - this.mouse_pos['y'];
            this.element.move(dx, dy);
            var pos = this.element.get_position();
            if(pos.x - this.r <= 0) {
            	pos.x = this.r + 1;
            } else {
            	if(pos.x + this.r >= this.canvas.width) {
            		pos.x = this.canvas.width - this.r - 1;
            	}
            }
            if(pos.y - this.r <= 0) {
            	pos.y = this.r + 1;
            } else {
            	if(pos.y + this.r >= this.canvas.height) {
            		pos.y = this.canvas.height - this.r - 1;
            	}
            }
            this.element.set_position(pos.x, pos.y);
            this.mouse_pos = {'x':x, 'y':y};
            this.vel = {'x':(1 - this.smooth) * dx + this.smooth * this.vel['x'], 'y':(1 - this.smooth) * dy + this.smooth * this.vel['y']};
            this.enter_Root_main_behaviour_dragging();
        }
        catched = true;
    }
    
    return catched;
};

Ball.prototype.transition_Root_main_behaviour_selected = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "mouse_press" && event.port === "ball_ui") {
        var parameters = event.parameters;
        
        var x = parameters[0];
        
        var y = parameters[1];
        
        var button = parameters[2];
        if (button == ui.MOUSE_BUTTONS.LEFT) {
            enableds.push(1);
        }
    }
    
    if (event.name === "key_press" && event.port === "ui") {
        var parameters = event.parameters;
        
        var key = parameters[0];
        
        var active_window = parameters[1];
        if (key == ui.KEYCODES.DELETE && active_window == this.field_window) {
            enableds.push(2);
        }
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_main_behaviour_selected. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            var parameters = event.parameters;
            
            var x = parameters[0];
            
            var y = parameters[1];
            
            var button = parameters[2];
            this.exit_Root_main_behaviour_selected();
            this.mouse_pos = {'x':x, 'y':y};
            this.enter_Root_main_behaviour_dragging();
        }
        else if (enabled === 2) {
            var parameters = event.parameters;
            
            var key = parameters[0];
            
            var active_window = parameters[1];
            this.exit_Root_main_behaviour_selected();
            this.addEvent(new Event("delete_self", null, []));
            this.enter_Root_main_behaviour_selected();
        }
        catched = true;
    }
    
    return catched;
};

Ball.prototype.transition_Root_main_behaviour_initializing = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "set_association_name") {
        enableds.push(1);
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_main_behaviour_initializing. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            var parameters = event.parameters;
            
            var association_name = parameters[0];
            this.exit_Root_main_behaviour_initializing();
            this.association_name = association_name;
            this.enter_Root_main_behaviour_bouncing();
        }
        catched = true;
    }
    
    return catched;
};

Ball.prototype.transition_Root_main_behaviour_bouncing = function(event) {
    var catched = false;
    var enableds = new Array();
    if (event.name === "_0after") {
        enableds.push(1);
    }
    
    if (event.name === "mouse_press" && event.port === "ball_ui") {
        var parameters = event.parameters;
        
        var x = parameters[0];
        
        var y = parameters[1];
        
        var button = parameters[2];
        if (button == ui.MOUSE_BUTTONS.LEFT) {
            enableds.push(2);
        }
    }
    
    if (enableds.length > 1) {
        console.log("Runtime warning : indeterminism detected in a transition from node Root_main_behaviour_bouncing. Only the first in document order enabled transition is executed.")
    }
    
    if (enableds.length > 0) {
        var enabled = enableds[0];
        if (enabled === 1) {
            this.exit_Root_main_behaviour_bouncing();
            var pos = this.element.get_position();
            if(pos.x - this.r <= 0 || pos.x + this.r >= this.canvas.width) {
            	this.vel['x'] = -this.vel['x'];
            }
            if(pos.y - this.r <= 0 || pos.y + this.r >= this.canvas.height) {
            	this.vel['y'] = -this.vel['y'];
            }
            this.element.move(this.vel['x'], this.vel['y']);
            this.enter_Root_main_behaviour_bouncing();
        }
        else if (enabled === 2) {
            var parameters = event.parameters;
            
            var x = parameters[0];
            
            var y = parameters[1];
            
            var button = parameters[2];
            this.exit_Root_main_behaviour_bouncing();
            this.element.set_color('#ff0');
            this.enter_Root_main_behaviour_selected();
        }
        catched = true;
    }
    
    return catched;
};

Ball.prototype.transition_Root_deleted = function(event) {
    var catched = false;
    return catched;
};

// Execute transitions
Ball.prototype.transition = function(event) {
    if (!event) event = new Event();
    this.state_changed = this.transition_Root(event);
};

// inState method for statechart
Ball.prototype.inState = function(nodes) {
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

Ball.prototype.commonConstructor = function(controller) {
    if (!controller) controller = null;
    // Constructor part that is common for all constructors.
    RuntimeClassBase.call(this);
    
    // User defined input ports
    this.inports = new Object();
    this.inports["ball_ui"] = controller.addInputPort("ball_ui", this);
    
    // User defined attributes
    this.field_window = null;
    this.canvas = null;
    this.element = null;
    
    this.controller = controller;
    this.object_manager = (controller == null ? null : controller.object_manager);
    this.current_state = new Object();
    this.history_state = new Object();
    this.timers = new Object();
    
    // Initialize statechart
    this.current_state[this.Root] = new Array();
    this.current_state[this.Root_main_behaviour] = new Array();
};

Ball.prototype.start = function() {
    RuntimeClassBase.prototype.start.call(this);
    this.enterDefault_Root_main_behaviour();
};

// put class in global diagram object
Bouncing_Balls.Ball = Ball;

var ObjectManager = function(controller) {
    ObjectManagerBase.call(this, controller);
};

ObjectManager.prototype = new ObjectManagerBase();

ObjectManager.prototype.instantiate = function(class_name, construct_params) {
    if (class_name === "Button") {
        var instance = new Button(this.controller, construct_params[0], construct_params[1], construct_params[2]);
        instance.associations = new Object();
        instance.associations["parent"] = new Association("Field", 1, 1);
    } else if (class_name === "Field") {
        var instance = new Field(this.controller);
        instance.associations = new Object();
        instance.associations["parent"] = new Association("MainApp", 1, 1);
        instance.associations["buttons"] = new Association("Button", 0, -1);
        instance.associations["balls"] = new Association("Ball", 0, -1);
    } else if (class_name === "MainApp") {
        var instance = new MainApp(this.controller);
        instance.associations = new Object();
        instance.associations["fields"] = new Association("Field", 0, -1);
    } else if (class_name === "Ball") {
        var instance = new Ball(this.controller, construct_params[0], construct_params[1], construct_params[2], construct_params[3]);
        instance.associations = new Object();
        instance.associations["parent"] = new Association("Field", 1, 1);
    }
    return instance;
};

// put in global diagram object
Bouncing_Balls.ObjectManager = ObjectManager;

var Controller = function(keep_running, finished_callback) {
    if (keep_running === undefined) keep_running = true;
    JsEventLoopControllerBase.call(this, new ObjectManager(this), keep_running, finished_callback);
    this.addInputPort("field_ui");
    this.addInputPort("ball_ui");
    this.addInputPort("ui");
    this.object_manager.createInstance("MainApp", []);
};

Controller.prototype = new JsEventLoopControllerBase();

// put in global diagram object
Bouncing_Balls.Controller = Controller;

})();
