/* Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Tue Aug 09 09:35:53 2016

Model author: Glenn De Jonghe
Model name:   TestInstate
Model description:
Testing the INSTATE macro.*/


// package "TestInstate"
var TestInstate = {};
(function() {

var Class1 = function(controller) {
    RuntimeClassBase.call(this, controller);
    
    this.semantics.big_step_maximality = StatechartSemantics.TakeOne;
    this.semantics.internal_event_lifeline = StatechartSemantics.NextSmallStep;
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
    
    // state /parallel_1
    this.states["/parallel_1"] = new ParallelState(1, this);
    
    // state /parallel_1/orthogonal1
    this.states["/parallel_1/orthogonal1"] = new State(2, this);
    
    // state /parallel_1/orthogonal1/state1
    this.states["/parallel_1/orthogonal1/state1"] = new State(3, this);
    
    // state /parallel_1/orthogonal1/inner
    this.states["/parallel_1/orthogonal1/inner"] = new State(4, this);
    
    // state /parallel_1/orthogonal1/inner/state2
    this.states["/parallel_1/orthogonal1/inner/state2"] = new State(5, this);
    
    // state /parallel_1/orthogonal1/inner/state3
    this.states["/parallel_1/orthogonal1/inner/state3"] = new State(6, this);
    
    // state /parallel_1/orthogonal2
    this.states["/parallel_1/orthogonal2"] = new State(7, this);
    
    // state /parallel_1/orthogonal2/tester
    this.states["/parallel_1/orthogonal2/tester"] = new State(8, this);
    
    // state /parallel_1/orthogonal2/stop
    this.states["/parallel_1/orthogonal2/stop"] = new State(9, this);
    
    // add children
    this.states[""].addChild(this.states["/parallel_1"]);
    this.states["/parallel_1"].addChild(this.states["/parallel_1/orthogonal1"]);
    this.states["/parallel_1"].addChild(this.states["/parallel_1/orthogonal2"]);
    this.states["/parallel_1/orthogonal1"].addChild(this.states["/parallel_1/orthogonal1/state1"]);
    this.states["/parallel_1/orthogonal1"].addChild(this.states["/parallel_1/orthogonal1/inner"]);
    this.states["/parallel_1/orthogonal1/inner"].addChild(this.states["/parallel_1/orthogonal1/inner/state2"]);
    this.states["/parallel_1/orthogonal1/inner"].addChild(this.states["/parallel_1/orthogonal1/inner/state3"]);
    this.states["/parallel_1/orthogonal2"].addChild(this.states["/parallel_1/orthogonal2/tester"]);
    this.states["/parallel_1/orthogonal2"].addChild(this.states["/parallel_1/orthogonal2/stop"]);
    this.states[""].fixTree();
    this.states[""].default_state = this.states["/parallel_1"];
    this.states["/parallel_1/orthogonal1"].default_state = this.states["/parallel_1/orthogonal1/state1"];
    this.states["/parallel_1/orthogonal1/inner"].default_state = this.states["/parallel_1/orthogonal1/inner/state2"];
    this.states["/parallel_1/orthogonal2"].default_state = this.states["/parallel_1/orthogonal2/tester"];
    
    // transition /parallel_1/orthogonal1/state1
    var _parallel_1_orthogonal1_state1_0 = new Transition(this, this.states["/parallel_1/orthogonal1/state1"], [this.states["/parallel_1/orthogonal1/inner"]]);
    _parallel_1_orthogonal1_state1_0.setTrigger(new Event("to_inner", null));
    this.states["/parallel_1/orthogonal1/state1"].addTransition(_parallel_1_orthogonal1_state1_0);
    
    // transition /parallel_1/orthogonal1/inner/state2
    var _parallel_1_orthogonal1_inner_state2_0 = new Transition(this, this.states["/parallel_1/orthogonal1/inner/state2"], [this.states["/parallel_1/orthogonal1/inner/state3"]]);
    _parallel_1_orthogonal1_inner_state2_0.setTrigger(new Event("to_state3", null));
    this.states["/parallel_1/orthogonal1/inner/state2"].addTransition(_parallel_1_orthogonal1_inner_state2_0);
    
    // transition /parallel_1/orthogonal2/tester
    var _parallel_1_orthogonal2_tester_0 = new Transition(this, this.states["/parallel_1/orthogonal2/tester"], [this.states["/parallel_1/orthogonal2/tester"]]);
    _parallel_1_orthogonal2_tester_0.setAction(this._parallel_1_orthogonal2_tester_0_exec);
    _parallel_1_orthogonal2_tester_0.setTrigger(null);
    _parallel_1_orthogonal2_tester_0.setGuard(this._parallel_1_orthogonal2_tester_0_guard);
    this.states["/parallel_1/orthogonal2/tester"].addTransition(_parallel_1_orthogonal2_tester_0);
    var _parallel_1_orthogonal2_tester_1 = new Transition(this, this.states["/parallel_1/orthogonal2/tester"], [this.states["/parallel_1/orthogonal2/tester"]]);
    _parallel_1_orthogonal2_tester_1.setAction(this._parallel_1_orthogonal2_tester_1_exec);
    _parallel_1_orthogonal2_tester_1.setTrigger(null);
    _parallel_1_orthogonal2_tester_1.setGuard(this._parallel_1_orthogonal2_tester_1_guard);
    this.states["/parallel_1/orthogonal2/tester"].addTransition(_parallel_1_orthogonal2_tester_1);
    var _parallel_1_orthogonal2_tester_2 = new Transition(this, this.states["/parallel_1/orthogonal2/tester"], [this.states["/parallel_1/orthogonal2/stop"]]);
    _parallel_1_orthogonal2_tester_2.setAction(this._parallel_1_orthogonal2_tester_2_exec);
    _parallel_1_orthogonal2_tester_2.setTrigger(null);
    _parallel_1_orthogonal2_tester_2.setGuard(this._parallel_1_orthogonal2_tester_2_guard);
    this.states["/parallel_1/orthogonal2/tester"].addTransition(_parallel_1_orthogonal2_tester_2);
};

Class1.prototype._parallel_1_orthogonal2_tester_0_exec = function(parameters) {
    this.big_step.outputEvent(new Event("check1", "test_output", new Array()));
    this.raiseInternalEvent(new Event("to_inner", null, new Array()));
};

Class1.prototype._parallel_1_orthogonal2_tester_0_guard = function(parameters) {
    return this.inState(["/parallel_1/orthogonal1/state1"]);
};

Class1.prototype._parallel_1_orthogonal2_tester_1_exec = function(parameters) {
    this.big_step.outputEvent(new Event("check2", "test_output", new Array()));
    this.raiseInternalEvent(new Event("to_state3", null, new Array()));
};

Class1.prototype._parallel_1_orthogonal2_tester_1_guard = function(parameters) {
    return this.inState(["/parallel_1/orthogonal1/inner/state2"]);
};

Class1.prototype._parallel_1_orthogonal2_tester_2_exec = function(parameters) {
    this.big_step.outputEvent(new Event("check3", "test_output", new Array()));
};

Class1.prototype._parallel_1_orthogonal2_tester_2_guard = function(parameters) {
    return this.inState(["/parallel_1/orthogonal1/inner/state3"]);
};

Class1.prototype.initializeStatechart = function() {
    // enter default state
    this.default_targets = this.states["/parallel_1"].getEffectiveTargetStates();
    RuntimeClassBase.prototype.initializeStatechart.call(this);
};

// add symbol 'Class1' to package 'TestInstate'
TestInstate.Class1 = Class1;

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

// add symbol 'ObjectManager' to package 'TestInstate'
TestInstate.ObjectManager = ObjectManager;

var Controller = function(event_loop_callbacks, finished_callback, behind_schedule_callback) {
    if (finished_callback === undefined) finished_callback = null;
    if (behind_schedule_callback === undefined) behind_schedule_callback = null;
    EventLoopControllerBase.call(this, new ObjectManager(this), event_loop_callbacks, finished_callback, behind_schedule_callback);
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

// add symbol 'Controller' to package 'TestInstate'
TestInstate.Controller = Controller;

var InputEvent = function(name, port, parameters, time_offset) {
    this.name = name;
    this.port = port;
    this.parameters = parameters;
    this.time_offset = time_offset;
};

// add symbol 'InputEvent' to package 'TestInstate'
TestInstate.InputEvent = InputEvent;

var Test = function() {
};
Test.prototype.input_events = new Array();
Test.prototype.expected_events = [[new Event("check1", "test_output", new Array())], [new Event("check2", "test_output", new Array())], [new Event("check3", "test_output", new Array())]];

// add symbol 'Test' to package 'TestInstate'
TestInstate.Test = Test;
})();