/* Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Tue Aug 09 09:35:54 2016

Model author: Herr Joeri Exelmans
Model name:   source_child
Model description:
'Source Child' priority-semantics: If 2 transitions are enabled, and the source state of the first is an ancestor of the second, only the second is executed.*/


// package "source_child"
var source_child = {};
(function() {

var c = function(controller) {
    RuntimeClassBase.call(this, controller);
    
    this.semantics.big_step_maximality = StatechartSemantics.TakeMany;
    this.semantics.internal_event_lifeline = StatechartSemantics.Queue;
    this.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep;
    this.semantics.priority = StatechartSemantics.SourceChild;
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
    
    // state /parent
    this.states["/parent"] = new State(1, this);
    this.states["/parent"].setEnter(this._parent_enter);
    
    // state /parent/a
    this.states["/parent/a"] = new State(2, this);
    this.states["/parent/a"].setEnter(this._parent_a_enter);
    
    // state /parent/b
    this.states["/parent/b"] = new State(3, this);
    this.states["/parent/b"].setEnter(this._parent_b_enter);
    
    // state /c
    this.states["/c"] = new State(4, this);
    this.states["/c"].setEnter(this._c_enter);
    
    // add children
    this.states[""].addChild(this.states["/parent"]);
    this.states[""].addChild(this.states["/c"]);
    this.states["/parent"].addChild(this.states["/parent/a"]);
    this.states["/parent"].addChild(this.states["/parent/b"]);
    this.states[""].fixTree();
    this.states[""].default_state = this.states["/parent"];
    this.states["/parent"].default_state = this.states["/parent/a"];
    
    // transition /parent/a
    var _parent_a_0 = new Transition(this, this.states["/parent/a"], [this.states["/parent/b"]]);
    _parent_a_0.setTrigger(null);
    this.states["/parent/a"].addTransition(_parent_a_0);
    
    // transition /parent
    var _parent_0 = new Transition(this, this.states["/parent"], [this.states["/c"]]);
    _parent_0.setTrigger(null);
    this.states["/parent"].addTransition(_parent_0);
};

c.prototype._parent_enter = function() {
    this.big_step.outputEvent(new Event("entered_parent", "out", new Array()));
};

c.prototype._parent_a_enter = function() {
    this.big_step.outputEvent(new Event("entered_a", "out", new Array()));
};

c.prototype._parent_b_enter = function() {
    this.big_step.outputEvent(new Event("entered_b", "out", new Array()));
};

c.prototype._c_enter = function() {
    this.big_step.outputEvent(new Event("entered_c", "out", new Array()));
};

c.prototype.initializeStatechart = function() {
    // enter default state
    this.default_targets = this.states["/parent"].getEffectiveTargetStates();
    RuntimeClassBase.prototype.initializeStatechart.call(this);
};

// add symbol 'c' to package 'source_child'
source_child.c = c;

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

// add symbol 'ObjectManager' to package 'source_child'
source_child.ObjectManager = ObjectManager;

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

// add symbol 'Controller' to package 'source_child'
source_child.Controller = Controller;

var InputEvent = function(name, port, parameters, time_offset) {
    this.name = name;
    this.port = port;
    this.parameters = parameters;
    this.time_offset = time_offset;
};

// add symbol 'InputEvent' to package 'source_child'
source_child.InputEvent = InputEvent;

var Test = function() {
};
Test.prototype.input_events = new Array();
Test.prototype.expected_events = [[new Event("entered_parent", "out", new Array()), new Event("entered_a", "out", new Array())], [new Event("entered_b", "out", new Array()), new Event("entered_c", "out", new Array())]];

// add symbol 'Test' to package 'source_child'
source_child.Test = Test;
})();