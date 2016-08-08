/* Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Mon Aug 08 09:49:19 2016

Model author: Glenn De Jonghe
Model name:   TestObjectManager
Model description:
Testing the object manager*/


// package "TestObjectManager"
var TestObjectManager = {};
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
    
    // state /start
    this.states["/start"] = new State(1, this);
    
    // state /wait
    this.states["/wait"] = new State(2, this);
    
    // add children
    this.states[""].addChild(this.states["/start"]);
    this.states[""].addChild(this.states["/wait"]);
    this.states[""].fixTree();
    this.states[""].default_state = this.states["/start"];
    
    // transition /start
    var _start_0 = new Transition(this, this.states["/start"], [this.states["/wait"]]);
    _start_0.setAction(this._start_0_exec);
    _start_0.setTrigger(new Event("create", "test_input"));
    this.states["/start"].addTransition(_start_0);
    
    // transition /wait
    var _wait_0 = new Transition(this, this.states["/wait"], [this.states["/start"]]);
    _wait_0.setAction(this._wait_0_exec);
    _wait_0.setTrigger(new Event("instance_created", null));
    this.states["/wait"].addTransition(_wait_0);
};

Class1.prototype._start_0_exec = function(parameters) {
    this.big_step.outputEventOM(new Event("create_instance", null, [this, "test2_association"]));
    this.big_step.outputEvent(new Event("request_send", "test_output", new Array()));
};

Class1.prototype._wait_0_exec = function(parameters) {
    var association_name = parameters[0];
    this.big_step.outputEvent(new Event("instance_created", "test_output", new Array()));
    this.big_step.outputEventOM(new Event("start_instance", null, [this, "test2_association"]));
    this.big_step.outputEventOM(new Event("narrow_cast", null, [this, "test2_association", new Event("hello", null, new Array())]));
};

Class1.prototype.initializeStatechart = function() {
    // enter default state
    var states = this.states["/start"].getEffectiveTargetStates();
    this.updateConfiguration(states);
    for (var state_idx in states) {
        if (!states.hasOwnProperty(state_idx)) continue;
        var state = states[state_idx]
        if (state.enter) {
            state.enter();
        }
    }
};

// add symbol 'Class1' to package 'TestObjectManager'
TestObjectManager.Class1 = Class1;

var Class2 = function(controller) {
    RuntimeClassBase.call(this, controller);
    
    this.semantics.big_step_maximality = StatechartSemantics.TakeMany;
    this.semantics.internal_event_lifeline = StatechartSemantics.Queue;
    this.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep;
    this.semantics.priority = StatechartSemantics.SourceParent;
    this.semantics.concurrency = StatechartSemantics.Single;
    
    // build Statechart structure
    this.build_statechart_structure();
    
    // call user defined constructor
    Class2.prototype.user_defined_constructor.call(this);
};
Class2.prototype = new Object();
(function() {
    var proto = new RuntimeClassBase();
    for (prop in proto) {
        Class2.prototype[prop] = proto[prop];
    }
})();

Class2.prototype.user_defined_constructor = function() {
};

Class2.prototype.user_defined_destructor = function() {
};


// builds Statechart structure
Class2.prototype.build_statechart_structure = function() {
    
    // state <root>
    this.states[""] = new State(0, this);
    
    // state /start
    this.states["/start"] = new State(1, this);
    
    // add children
    this.states[""].addChild(this.states["/start"]);
    this.states[""].fixTree();
    this.states[""].default_state = this.states["/start"];
    
    // transition /start
    var _start_0 = new Transition(this, this.states["/start"], [this.states["/start"]]);
    _start_0.setAction(this._start_0_exec);
    _start_0.setTrigger(new Event("hello", null));
    this.states["/start"].addTransition(_start_0);
};

Class2.prototype._start_0_exec = function(parameters) {
    this.big_step.outputEvent(new Event("second_working", "test_output", new Array()));
};

Class2.prototype.initializeStatechart = function() {
    // enter default state
    var states = this.states["/start"].getEffectiveTargetStates();
    this.updateConfiguration(states);
    for (var state_idx in states) {
        if (!states.hasOwnProperty(state_idx)) continue;
        var state = states[state_idx]
        if (state.enter) {
            state.enter();
        }
    }
};

// add symbol 'Class2' to package 'TestObjectManager'
TestObjectManager.Class2 = Class2;

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
        instance.associations["test2_association"] = new Association("Class2", 0, -1);
    } else if (class_name === "Class2") {
        var instance = new Class2(this.controller);
        instance.associations = new Object();
    } else  {
        throw new Error("Cannot instantiate class " + class_name);
    }
    return instance;
};

// add symbol 'ObjectManager' to package 'TestObjectManager'
TestObjectManager.ObjectManager = ObjectManager;

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

// add symbol 'Controller' to package 'TestObjectManager'
TestObjectManager.Controller = Controller;

var InputEvent = function(name, port, parameters, time_offset) {
    this.name = name;
    this.port = port;
    this.parameters = parameters;
    this.time_offset = time_offset;
};

// add symbol 'InputEvent' to package 'TestObjectManager'
TestObjectManager.InputEvent = InputEvent;

var Test = function() {
};
Test.prototype.input_events = [new InputEvent("create", "test_input", new Array(), 0.0)];
Test.prototype.expected_events = [[new Event("request_send", "test_output", new Array())], [new Event("instance_created", "test_output", new Array())], [new Event("second_working", "test_output", new Array())]];

// add symbol 'Test' to package 'TestObjectManager'
TestObjectManager.Test = Test;
})();