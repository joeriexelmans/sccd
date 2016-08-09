/* Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Tue Aug 09 09:35:52 2016

Model author: Glenn De Jonghe
Model name:   TestAfter
Model description:
Used for testing the AFTER event.*/


// package "TestAfter"
var TestAfter = {};
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
    
    // state /composite
    this.states["/composite"] = new State(1, this);
    
    // state /composite/state_1
    this.states["/composite/state_1"] = new State(2, this);
    this.states["/composite/state_1"].setEnter(this._composite_state_1_enter);
    this.states["/composite/state_1"].setExit(this._composite_state_1_exit);
    
    // state /composite/state_2
    this.states["/composite/state_2"] = new State(3, this);
    this.states["/composite/state_2"].setEnter(this._composite_state_2_enter);
    
    // state /composite/state_3
    this.states["/composite/state_3"] = new State(4, this);
    this.states["/composite/state_3"].setEnter(this._composite_state_3_enter);
    
    // add children
    this.states[""].addChild(this.states["/composite"]);
    this.states["/composite"].addChild(this.states["/composite/state_1"]);
    this.states["/composite"].addChild(this.states["/composite/state_2"]);
    this.states["/composite"].addChild(this.states["/composite/state_3"]);
    this.states[""].fixTree();
    this.states[""].default_state = this.states["/composite"];
    this.states["/composite"].default_state = this.states["/composite/state_1"];
    
    // transition /composite/state_1
    var _composite_state_1_0 = new Transition(this, this.states["/composite/state_1"], [this.states["/composite/state_2"]]);
    _composite_state_1_0.setTrigger(new Event("_0after"));
    this.states["/composite/state_1"].addTransition(_composite_state_1_0);
    var _composite_state_1_1 = new Transition(this, this.states["/composite/state_1"], [this.states["/composite/state_3"]]);
    _composite_state_1_1.setTrigger(new Event("_1after"));
    this.states["/composite/state_1"].addTransition(_composite_state_1_1);
};

Class1.prototype._composite_state_1_enter = function() {
    this.addTimer(0, 0.1);
    this.addTimer(1, 0.2);
};

Class1.prototype._composite_state_1_exit = function() {
    this.removeTimer(0);
    this.removeTimer(1);
};

Class1.prototype._composite_state_2_enter = function() {
    this.big_step.outputEvent(new Event("in_state_2", "test_output", new Array()));
};

Class1.prototype._composite_state_3_enter = function() {
    this.big_step.outputEvent(new Event("in_state_3", "test_output", new Array()));
};

Class1.prototype.initializeStatechart = function() {
    // enter default state
    this.default_targets = this.states["/composite"].getEffectiveTargetStates();
    RuntimeClassBase.prototype.initializeStatechart.call(this);
};

// add symbol 'Class1' to package 'TestAfter'
TestAfter.Class1 = Class1;

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

// add symbol 'ObjectManager' to package 'TestAfter'
TestAfter.ObjectManager = ObjectManager;

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

// add symbol 'Controller' to package 'TestAfter'
TestAfter.Controller = Controller;

var InputEvent = function(name, port, parameters, time_offset) {
    this.name = name;
    this.port = port;
    this.parameters = parameters;
    this.time_offset = time_offset;
};

// add symbol 'InputEvent' to package 'TestAfter'
TestAfter.InputEvent = InputEvent;

var Test = function() {
};
Test.prototype.input_events = new Array();
Test.prototype.expected_events = [[new Event("in_state_2", "test_output", new Array())]];

// add symbol 'Test' to package 'TestAfter'
TestAfter.Test = Test;
})();