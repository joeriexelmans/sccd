/* Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Mon Aug 08 09:49:18 2016

Model author: Yentl Van Tendeloo
Model name:   after_0
Model description:
Used for testing the AFTER(0) event---which should not block the deletion of the B instance.*/


// package "after_0"
var after_0 = {};
(function() {

var A = function(controller) {
    RuntimeClassBase.call(this, controller);
    
    this.semantics.big_step_maximality = StatechartSemantics.TakeMany;
    this.semantics.internal_event_lifeline = StatechartSemantics.Queue;
    this.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep;
    this.semantics.priority = StatechartSemantics.SourceParent;
    this.semantics.concurrency = StatechartSemantics.Single;
    
    // build Statechart structure
    this.build_statechart_structure();
    
    // call user defined constructor
    A.prototype.user_defined_constructor.call(this);
};
A.prototype = new Object();
(function() {
    var proto = new RuntimeClassBase();
    for (prop in proto) {
        A.prototype[prop] = proto[prop];
    }
})();

A.prototype.user_defined_constructor = function() {
};

A.prototype.user_defined_destructor = function() {
};


// builds Statechart structure
A.prototype.build_statechart_structure = function() {
    
    // state <root>
    this.states[""] = new State(0, this);
    
    // state /x
    this.states["/x"] = new State(1, this);
    this.states["/x"].setEnter(this._x_enter);
    
    // state /ready
    this.states["/ready"] = new State(2, this);
    this.states["/ready"].setEnter(this._ready_enter);
    
    // state /done
    this.states["/done"] = new State(3, this);
    
    // add children
    this.states[""].addChild(this.states["/x"]);
    this.states[""].addChild(this.states["/ready"]);
    this.states[""].addChild(this.states["/done"]);
    this.states[""].fixTree();
    this.states[""].default_state = this.states["/x"];
    
    // transition /x
    var _x_0 = new Transition(this, this.states["/x"], [this.states["/ready"]]);
    _x_0.setTrigger(new Event("instance_created", null));
    this.states["/x"].addTransition(_x_0);
    
    // transition /ready
    var _ready_0 = new Transition(this, this.states["/ready"], [this.states["/done"]]);
    _ready_0.setAction(this._ready_0_exec);
    _ready_0.setTrigger(new Event("close", null));
    this.states["/ready"].addTransition(_ready_0);
};

A.prototype._x_enter = function() {
    this.big_step.outputEventOM(new Event("create_instance", null, [this, 'child', 'B']));
    this.big_step.outputEvent(new Event("creating_instance", "test_output", new Array()));
};

A.prototype._ready_enter = function() {
    this.big_step.outputEventOM(new Event("start_instance", null, [this, 'child[0]']));
    this.big_step.outputEvent(new Event("starting_instance", "test_output", new Array()));
};

A.prototype._ready_0_exec = function(parameters) {
    this.big_step.outputEventOM(new Event("delete_instance", null, [this, 'child[0]']));
    this.big_step.outputEvent(new Event("deleting_instance", "test_output", new Array()));
};

A.prototype.initializeStatechart = function() {
    // enter default state
    var states = this.states["/x"].getEffectiveTargetStates();
    this.updateConfiguration(states);
    for (var state_idx in states) {
        if (!states.hasOwnProperty(state_idx)) continue;
        var state = states[state_idx]
        if (state.enter) {
            state.enter();
        }
    }
};

// add symbol 'A' to package 'after_0'
after_0.A = A;

var B = function(controller) {
    RuntimeClassBase.call(this, controller);
    
    this.semantics.big_step_maximality = StatechartSemantics.TakeMany;
    this.semantics.internal_event_lifeline = StatechartSemantics.Queue;
    this.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep;
    this.semantics.priority = StatechartSemantics.SourceParent;
    this.semantics.concurrency = StatechartSemantics.Single;
    
    // build Statechart structure
    this.build_statechart_structure();
    
    // call user defined constructor
    B.prototype.user_defined_constructor.call(this);
};
B.prototype = new Object();
(function() {
    var proto = new RuntimeClassBase();
    for (prop in proto) {
        B.prototype[prop] = proto[prop];
    }
})();

B.prototype.user_defined_constructor = function() {
};

B.prototype.user_defined_destructor = function() {
};


// builds Statechart structure
B.prototype.build_statechart_structure = function() {
    
    // state <root>
    this.states[""] = new State(0, this);
    
    // state /z
    this.states["/z"] = new State(1, this);
    this.states["/z"].setEnter(this._z_enter);
    this.states["/z"].setExit(this._z_exit);
    
    // add children
    this.states[""].addChild(this.states["/z"]);
    this.states[""].fixTree();
    this.states[""].default_state = this.states["/z"];
    
    // transition /z
    var _z_0 = new Transition(this, this.states["/z"], [this.states["/z"]]);
    _z_0.setAction(this._z_0_exec);
    _z_0.setTrigger(new Event("_0after"));
    this.states["/z"].addTransition(_z_0);
};

B.prototype._z_enter = function() {
    this.addTimer(0, 0);
};

B.prototype._z_exit = function() {
    this.removeTimer(0);
};

B.prototype._z_0_exec = function(parameters) {
    this.big_step.outputEventOM(new Event("broad_cast", null, [new Event("close", null, new Array())]));
    this.big_step.outputEvent(new Event("after_0", "test_output", new Array()));
};

B.prototype.initializeStatechart = function() {
    // enter default state
    var states = this.states["/z"].getEffectiveTargetStates();
    this.updateConfiguration(states);
    for (var state_idx in states) {
        if (!states.hasOwnProperty(state_idx)) continue;
        var state = states[state_idx]
        if (state.enter) {
            state.enter();
        }
    }
};

// add symbol 'B' to package 'after_0'
after_0.B = B;

var ObjectManager = function(controller) {
    ObjectManagerBase.call(this, controller);
};
ObjectManager.prototype = new Object();
(function() {
    var proto = new ObjectManagerBase();
    for (prop in proto) {
        ObjectManager.prototype[prop] = proto[prop];
    }
})();

ObjectManager.prototype.instantiate = function(class_name, construct_params) {
    if (class_name === "A") {
        var instance = new A(this.controller);
        instance.associations = new Object();
        instance.associations["child"] = new Association("B", 0, 1);
    } else if (class_name === "B") {
        var instance = new B(this.controller);
        instance.associations = new Object();
        instance.associations["parent"] = new Association("A", 1, 1);
    } else  {
        throw new Error("Cannot instantiate class " + class_name);
    }
    return instance;
};

// add symbol 'ObjectManager' to package 'after_0'
after_0.ObjectManager = ObjectManager;

var Controller = function(event_loop_callbacks, finished_callback, behind_schedule_callback) {
    if (finished_callback === undefined) finished_callback = null;
    if (behind_schedule_callback === undefined) behind_schedule_callback = null;
    EventLoopControllerBase.call(this, new ObjectManager(this), event_loop_callbacks, finished_callback, behind_schedule_callback);
    this.addOutputPort("test_output");
    this.object_manager.createInstance("A", new Array());
};
Controller.prototype = new Object();
(function() {
    var proto = new EventLoopControllerBase();
    for (prop in proto) {
        Controller.prototype[prop] = proto[prop];
    }
})();

// add symbol 'Controller' to package 'after_0'
after_0.Controller = Controller;

var InputEvent = function(name, port, parameters, time_offset) {
    this.name = name;
    this.port = port;
    this.parameters = parameters;
    this.time_offset = time_offset;
};

// add symbol 'InputEvent' to package 'after_0'
after_0.InputEvent = InputEvent;

var Test = function() {
};
Test.prototype.input_events = new Array();
Test.prototype.expected_events = [[new Event("creating_instance", "test_output", new Array())], [new Event("starting_instance", "test_output", new Array())], [new Event("after_0", "test_output", new Array())], [new Event("deleting_instance", "test_output", new Array()), new Event("after_0", "test_output", new Array())]];

// add symbol 'Test' to package 'after_0'
after_0.Test = Test;
})();