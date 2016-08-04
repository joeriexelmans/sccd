/* Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Thu Aug 04 12:51:02 2016

Model author: Herr Joeri Exelmans
Model name:   rapid
Model description:
After event with a very small timeout.*/


// package "rapid"
var rapid = {};
(function() {

var c = function(controller) {
    RuntimeClassBase.call(this, controller);
    
    this.semantics.big_step_maximality = StatechartSemantics.TakeMany;
    this.semantics.internal_event_lifeline = StatechartSemantics.Queue;
    this.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep;
    this.semantics.priority = StatechartSemantics.SourceParent;
    this.semantics.concurrency = StatechartSemantics.Single;
    
    // build Statechart structure
    this.build_statechart_structure();
    
    // user defined attributes
    this.i = null;
    
    // call user defined constructor
    c.prototype.user_defined_constructor.call(this);
};
c.prototype = new Object();
(function() {
    var proto = new RuntimeClassBase();
    for (prop in proto) {
        c.prototype[prop] = proto[prop];
    }
})();

c.prototype.user_defined_constructor = function() {
    this.i = 0;
};

c.prototype.user_defined_destructor = function() {
};


// builds Statechart structure
c.prototype.build_statechart_structure = function() {
    
    // state <root>
    this.states[""] = new State(0, this);
    
    // state /a
    this.states["/a"] = new State(1, this);
    this.states["/a"].setEnter(this._a_enter);
    this.states["/a"].setExit(this._a_exit);
    
    // add children
    this.states[""].addChild(this.states["/a"]);
    this.states[""].fixTree();
    this.states[""].default_state = this.states["/a"];
    
    // transition /a
    var _a_0 = new Transition(this, this.states["/a"], [this.states["/a"]]);
    _a_0.setAction(this._a_0_exec);
    _a_0.trigger = new Event("_0after");
    _a_0.setGuard(this._a_0_guard);
    this.states["/a"].addTransition(_a_0);
};

c.prototype._a_enter = function() {
    this.addTimer(0, 1e-10);
    this.big_step.outputEvent(new Event("entered_a", "out", new Array()));
};

c.prototype._a_exit = function() {
    this.removeTimer(0);
};

c.prototype._a_0_exec = function(parameters) {
    this.i++;
};

c.prototype._a_0_guard = function(parameters) {
    return this.i < 2;
};

c.prototype.initializeStatechart = function() {
    // enter default state
    var states = this.states["/a"].getEffectiveTargetStates();
    this.updateConfiguration(states);
    for (var state_idx in states) {
        if (!states.hasOwnProperty(state_idx)) continue;
        var state = states[state_idx]
        if (state.enter) {
            state.enter();
        }
    }
};

// add symbol 'c' to package 'rapid'
rapid.c = c;

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
    if (class_name === "c") {
        var instance = new c(this.controller);
        instance.associations = new Object();
    } else  {
        throw new Error("Cannot instantiate class " + class_name);
    }
    return instance;
};

// add symbol 'ObjectManager' to package 'rapid'
rapid.ObjectManager = ObjectManager;

var Controller = function(event_loop_callbacks, finished_callback) {
    if (finished_callback === undefined) finished_callback = null;
    EventLoopControllerBase.call(this, new ObjectManager(this), event_loop_callbacks, finished_callback);
    this.addInputPort("in");
    this.addOutputPort("out");
    this.object_manager.createInstance("c", new Array());
};
Controller.prototype = new Object();
(function() {
    var proto = new EventLoopControllerBase();
    for (prop in proto) {
        Controller.prototype[prop] = proto[prop];
    }
})();

// add symbol 'Controller' to package 'rapid'
rapid.Controller = Controller;

var InputEvent = function(name, port, parameters, time_offset) {
    this.name = name;
    this.port = port;
    this.parameters = parameters;
    this.time_offset = time_offset;
};

// add symbol 'InputEvent' to package 'rapid'
rapid.InputEvent = InputEvent;

var Test = function() {
};
Test.prototype.input_events = new Array();
Test.prototype.expected_events = [[new Event("entered_a", "out", new Array())], [new Event("entered_a", "out", new Array())], [new Event("entered_a", "out", new Array())]];

// add symbol 'Test' to package 'rapid'
rapid.Test = Test;
})();