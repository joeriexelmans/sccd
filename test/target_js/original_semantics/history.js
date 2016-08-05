/* Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Fri Aug 05 16:13:29 2016

Model author: Glenn De Jonghe
Model name:   TestHistory
Model description:
Testing the History state.*/


// package "TestHistory"
var TestHistory = {};
(function() {

var Class1 = function(controller) {
    RuntimeClassBase.call(this, controller);
    
    this.semantics.big_step_maximality = StatechartSemantics.TakeMany;
    this.semantics.internal_event_lifeline = StatechartSemantics.Queue;
    this.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep;
    this.semantics.priority = StatechartSemantics.SourceParent;
    this.semantics.concurrency = StatechartSemantics.Single;
    
    // build Statechart structure
    this.build_statechart_structure();
    
    // call user defined constructor
    Class1.prototype.user_defined_constructor.call(this);
};
Class1.prototype = new Object();
(function() {
    var proto = new RuntimeClassBase();
    for (prop in proto) {
        Class1.prototype[prop] = proto[prop];
    }
})();

Class1.prototype.user_defined_constructor = function() {
};

Class1.prototype.user_defined_destructor = function() {
};


// builds Statechart structure
Class1.prototype.build_statechart_structure = function() {
    
    // state <root>
    this.states[""] = new State(0, this);
    
    // state /composite_1
    this.states["/composite_1"] = new State(1, this);
    
    // state /composite_1/state_1
    this.states["/composite_1/state_1"] = new State(2, this);
    this.states["/composite_1/state_1"].setEnter(this._composite_1_state_1_enter);
    
    // state /composite_1/state_2
    this.states["/composite_1/state_2"] = new State(3, this);
    this.states["/composite_1/state_2"].setEnter(this._composite_1_state_2_enter);
    
    // state /composite_1/composite_history
    this.states["/composite_1/composite_history"] = new ShallowHistoryState(4, this);
    
    // state /state_3
    this.states["/state_3"] = new State(5, this);
    this.states["/state_3"].setEnter(this._state_3_enter);
    
    // add children
    this.states[""].addChild(this.states["/composite_1"]);
    this.states[""].addChild(this.states["/state_3"]);
    this.states["/composite_1"].addChild(this.states["/composite_1/state_1"]);
    this.states["/composite_1"].addChild(this.states["/composite_1/state_2"]);
    this.states["/composite_1"].addChild(this.states["/composite_1/composite_history"]);
    this.states[""].fixTree();
    this.states[""].default_state = this.states["/composite_1"];
    this.states["/composite_1"].default_state = this.states["/composite_1/state_1"];
    
    // transition /composite_1/state_1
    var _composite_1_state_1_0 = new Transition(this, this.states["/composite_1/state_1"], [this.states["/composite_1/state_2"]]);
    _composite_1_state_1_0.setTrigger(new Event("to_state_2", "test_input"));
    this.states["/composite_1/state_1"].addTransition(_composite_1_state_1_0);
    
    // transition /state_3
    var _state_3_0 = new Transition(this, this.states["/state_3"], [this.states["/composite_1/composite_history"]]);
    _state_3_0.setTrigger(null);
    this.states["/state_3"].addTransition(_state_3_0);
    
    // transition /composite_1
    var _composite_1_0 = new Transition(this, this.states["/composite_1"], [this.states["/state_3"]]);
    _composite_1_0.setTrigger(new Event("to_state_3", "test_input"));
    this.states["/composite_1"].addTransition(_composite_1_0);
};

Class1.prototype._composite_1_state_1_enter = function() {
    this.big_step.outputEvent(new Event("in_state_1", "test_output", new Array()));
};

Class1.prototype._composite_1_state_2_enter = function() {
    this.big_step.outputEvent(new Event("in_state_2", "test_output", new Array()));
};

Class1.prototype._state_3_enter = function() {
    this.big_step.outputEvent(new Event("in_state_3", "test_output", new Array()));
};

Class1.prototype.initializeStatechart = function() {
    // enter default state
    var states = this.states["/composite_1"].getEffectiveTargetStates();
    this.updateConfiguration(states);
    for (var state_idx in states) {
        if (!states.hasOwnProperty(state_idx)) continue;
        var state = states[state_idx]
        if (state.enter) {
            state.enter();
        }
    }
};

// add symbol 'Class1' to package 'TestHistory'
TestHistory.Class1 = Class1;

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
    if (class_name === "Class1") {
        var instance = new Class1(this.controller);
        instance.associations = new Object();
    } else  {
        throw new Error("Cannot instantiate class " + class_name);
    }
    return instance;
};

// add symbol 'ObjectManager' to package 'TestHistory'
TestHistory.ObjectManager = ObjectManager;

var Controller = function(event_loop_callbacks, finished_callback, behind_schedule_callback) {
    if (finished_callback === undefined) finished_callback = null;
    if (behind_schedule_callback === undefined) behind_schedule_callback = null;
    EventLoopControllerBase.call(this, new ObjectManager(this), event_loop_callbacks, finished_callback, behind_schedule_callback);
    this.addInputPort("test_input");
    this.addOutputPort("test_output");
    this.object_manager.createInstance("Class1", new Array());
};
Controller.prototype = new Object();
(function() {
    var proto = new EventLoopControllerBase();
    for (prop in proto) {
        Controller.prototype[prop] = proto[prop];
    }
})();

// add symbol 'Controller' to package 'TestHistory'
TestHistory.Controller = Controller;

var InputEvent = function(name, port, parameters, time_offset) {
    this.name = name;
    this.port = port;
    this.parameters = parameters;
    this.time_offset = time_offset;
};

// add symbol 'InputEvent' to package 'TestHistory'
TestHistory.InputEvent = InputEvent;

var Test = function() {
};
Test.prototype.input_events = [new InputEvent("to_state_2", "test_input", new Array(), 0.0), new InputEvent("to_state_3", "test_input", new Array(), 0.0)];
Test.prototype.expected_events = [[new Event("in_state_1", "test_output", new Array())], [new Event("in_state_2", "test_output", new Array())], [new Event("in_state_3", "test_output", new Array())], [new Event("in_state_2", "test_output", new Array())]];

// add symbol 'Test' to package 'TestHistory'
TestHistory.Test = Test;
})();