/* Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Thu Aug 04 12:51:02 2016

Model author: Herr Joeri Exelmans
Model name:   source_child_history
*/


// package "source_child_history"
var source_child_history = {};
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
    
    // state /main
    this.states["/main"] = new State(1, this);
    
    // state /main/history
    this.states["/main/history"] = new ShallowHistoryState(2, this);
    
    // state /main/A
    this.states["/main/A"] = new State(3, this);
    
    // state /main/B
    this.states["/main/B"] = new State(4, this);
    
    // add children
    this.states[""].addChild(this.states["/main"]);
    this.states["/main"].addChild(this.states["/main/history"]);
    this.states["/main"].addChild(this.states["/main/A"]);
    this.states["/main"].addChild(this.states["/main/B"]);
    this.states[""].fixTree();
    this.states[""].default_state = this.states["/main"];
    this.states["/main"].default_state = this.states["/main/A"];
    
    // transition /main/A
    var _main_A_0 = new Transition(this, this.states["/main/A"], [this.states["/main/B"]]);
    _main_A_0.setAction(this._main_A_0_exec);
    _main_A_0.trigger = new Event("e", "in");
    this.states["/main/A"].addTransition(_main_A_0);
    
    // transition /main
    var _main_0 = new Transition(this, this.states["/main"], [this.states["/main/history"]]);
    _main_0.setAction(this._main_0_exec);
    _main_0.trigger = new Event("e", "in");
    this.states["/main"].addTransition(_main_0);
};

c.prototype._main_0_exec = function(parameters) {
    this.big_step.outputEvent(new Event("to_history", "out", new Array()));
};

c.prototype._main_A_0_exec = function(parameters) {
    this.big_step.outputEvent(new Event("to_B", "out", new Array()));
};

c.prototype.initializeStatechart = function() {
    // enter default state
    var states = this.states["/main"].getEffectiveTargetStates();
    this.updateConfiguration(states);
    for (var state_idx in states) {
        if (!states.hasOwnProperty(state_idx)) continue;
        var state = states[state_idx]
        if (state.enter) {
            state.enter();
        }
    }
};

// add symbol 'c' to package 'source_child_history'
source_child_history.c = c;

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

// add symbol 'ObjectManager' to package 'source_child_history'
source_child_history.ObjectManager = ObjectManager;

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

// add symbol 'Controller' to package 'source_child_history'
source_child_history.Controller = Controller;

var InputEvent = function(name, port, parameters, time_offset) {
    this.name = name;
    this.port = port;
    this.parameters = parameters;
    this.time_offset = time_offset;
};

// add symbol 'InputEvent' to package 'source_child_history'
source_child_history.InputEvent = InputEvent;

var Test = function() {
};
Test.prototype.input_events = [new InputEvent("e", "in", new Array(), 0.0)];
Test.prototype.expected_events = [[new Event("to_B", "out", new Array())]];

// add symbol 'Test' to package 'source_child_history'
source_child_history.Test = Test;
})();