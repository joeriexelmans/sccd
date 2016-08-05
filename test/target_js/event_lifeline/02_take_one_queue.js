/* Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Fri Aug 05 16:13:26 2016

Model author: Herr Joeri Exelmans
Model name:   take_one_queue
Model description:
Internal event lifeline - Queue-semantics: Internal events are treated just like external events: They are added to the object's event queue and will be sensed in another big step. This way, a raised internal event will always be sensed at some point later in time, but it is possible that other (external) events in the object's event queue are treated first.*/


// package "take_one_queue"
var take_one_queue = {};
(function() {

var c = function(controller) {
    RuntimeClassBase.call(this, controller);
    
    this.semantics.big_step_maximality = StatechartSemantics.TakeOne;
    this.semantics.internal_event_lifeline = StatechartSemantics.Queue;
    this.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep;
    this.semantics.priority = StatechartSemantics.SourceParent;
    this.semantics.concurrency = StatechartSemantics.Single;
    
    // build Statechart structure
    this.build_statechart_structure();
    
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
    
    // state /b
    this.states["/b"] = new State(2, this);
    this.states["/b"].setEnter(this._b_enter);
    
    // state /c
    this.states["/c"] = new State(3, this);
    this.states["/c"].setEnter(this._c_enter);
    
    // add children
    this.states[""].addChild(this.states["/a"]);
    this.states[""].addChild(this.states["/b"]);
    this.states[""].addChild(this.states["/c"]);
    this.states[""].fixTree();
    this.states[""].default_state = this.states["/a"];
    
    // transition /a
    var _a_0 = new Transition(this, this.states["/a"], [this.states["/b"]]);
    _a_0.setAction(this._a_0_exec);
    _a_0.setTrigger(new Event("e", "in"));
    this.states["/a"].addTransition(_a_0);
    
    // transition /b
    var _b_0 = new Transition(this, this.states["/b"], [this.states["/c"]]);
    _b_0.setTrigger(new Event("f", null));
    this.states["/b"].addTransition(_b_0);
};

c.prototype._a_enter = function() {
    this.big_step.outputEvent(new Event("entered_a", "out", new Array()));
};

c.prototype._b_enter = function() {
    this.big_step.outputEvent(new Event("entered_b", "out", new Array()));
};

c.prototype._c_enter = function() {
    this.big_step.outputEvent(new Event("entered_c", "out", new Array()));
};

c.prototype._a_0_exec = function(parameters) {
    this.raiseInternalEvent(new Event("f", null, new Array()));
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

// add symbol 'c' to package 'take_one_queue'
take_one_queue.c = c;

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

// add symbol 'ObjectManager' to package 'take_one_queue'
take_one_queue.ObjectManager = ObjectManager;

var Controller = function(event_loop_callbacks, finished_callback, behind_schedule_callback) {
    if (finished_callback === undefined) finished_callback = null;
    if (behind_schedule_callback === undefined) behind_schedule_callback = null;
    EventLoopControllerBase.call(this, new ObjectManager(this), event_loop_callbacks, finished_callback, behind_schedule_callback);
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

// add symbol 'Controller' to package 'take_one_queue'
take_one_queue.Controller = Controller;

var InputEvent = function(name, port, parameters, time_offset) {
    this.name = name;
    this.port = port;
    this.parameters = parameters;
    this.time_offset = time_offset;
};

// add symbol 'InputEvent' to package 'take_one_queue'
take_one_queue.InputEvent = InputEvent;

var Test = function() {
};
Test.prototype.input_events = [new InputEvent("e", "in", new Array(), 0.0)];
Test.prototype.expected_events = [[new Event("entered_a", "out", new Array())], [new Event("entered_b", "out", new Array())], [new Event("entered_c", "out", new Array())]];

// add symbol 'Test' to package 'take_one_queue'
take_one_queue.Test = Test;
})();