/* Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Fri Aug 05 16:13:26 2016

Model author: Herr Joeri Exelmans
Model name:   orthogonal_take_one
Model description:
Take One-semantics: Each big step, a transition in each orthogonal component is made.*/


// package "orthogonal_take_one"
var orthogonal_take_one = {};
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
    
    // state /p
    this.states["/p"] = new ParallelState(1, this);
    
    // state /p/o0
    this.states["/p/o0"] = new State(2, this);
    
    // state /p/o0/sa
    this.states["/p/o0/sa"] = new State(3, this);
    this.states["/p/o0/sa"].setEnter(this._p_o0_sa_enter);
    
    // state /p/o0/sb
    this.states["/p/o0/sb"] = new State(4, this);
    this.states["/p/o0/sb"].setEnter(this._p_o0_sb_enter);
    
    // state /p/o0/sc
    this.states["/p/o0/sc"] = new State(5, this);
    this.states["/p/o0/sc"].setEnter(this._p_o0_sc_enter);
    
    // state /p/o1
    this.states["/p/o1"] = new State(6, this);
    
    // state /p/o1/sd
    this.states["/p/o1/sd"] = new State(7, this);
    this.states["/p/o1/sd"].setEnter(this._p_o1_sd_enter);
    
    // state /p/o1/se
    this.states["/p/o1/se"] = new State(8, this);
    this.states["/p/o1/se"].setEnter(this._p_o1_se_enter);
    
    // state /p/o1/sf
    this.states["/p/o1/sf"] = new State(9, this);
    this.states["/p/o1/sf"].setEnter(this._p_o1_sf_enter);
    
    // add children
    this.states[""].addChild(this.states["/p"]);
    this.states["/p"].addChild(this.states["/p/o0"]);
    this.states["/p"].addChild(this.states["/p/o1"]);
    this.states["/p/o0"].addChild(this.states["/p/o0/sa"]);
    this.states["/p/o0"].addChild(this.states["/p/o0/sb"]);
    this.states["/p/o0"].addChild(this.states["/p/o0/sc"]);
    this.states["/p/o1"].addChild(this.states["/p/o1/sd"]);
    this.states["/p/o1"].addChild(this.states["/p/o1/se"]);
    this.states["/p/o1"].addChild(this.states["/p/o1/sf"]);
    this.states[""].fixTree();
    this.states[""].default_state = this.states["/p"];
    this.states["/p/o0"].default_state = this.states["/p/o0/sa"];
    this.states["/p/o1"].default_state = this.states["/p/o1/sd"];
    
    // transition /p/o0/sa
    var _p_o0_sa_0 = new Transition(this, this.states["/p/o0/sa"], [this.states["/p/o0/sb"]]);
    _p_o0_sa_0.setTrigger(null);
    this.states["/p/o0/sa"].addTransition(_p_o0_sa_0);
    
    // transition /p/o0/sb
    var _p_o0_sb_0 = new Transition(this, this.states["/p/o0/sb"], [this.states["/p/o0/sc"]]);
    _p_o0_sb_0.setTrigger(null);
    this.states["/p/o0/sb"].addTransition(_p_o0_sb_0);
    
    // transition /p/o1/sd
    var _p_o1_sd_0 = new Transition(this, this.states["/p/o1/sd"], [this.states["/p/o1/se"]]);
    _p_o1_sd_0.setTrigger(null);
    this.states["/p/o1/sd"].addTransition(_p_o1_sd_0);
    
    // transition /p/o1/se
    var _p_o1_se_0 = new Transition(this, this.states["/p/o1/se"], [this.states["/p/o1/sf"]]);
    _p_o1_se_0.setTrigger(null);
    this.states["/p/o1/se"].addTransition(_p_o1_se_0);
};

c.prototype._p_o0_sa_enter = function() {
    this.big_step.outputEvent(new Event("entered_sa", "out", new Array()));
};

c.prototype._p_o0_sb_enter = function() {
    this.big_step.outputEvent(new Event("entered_sb", "out", new Array()));
};

c.prototype._p_o0_sc_enter = function() {
    this.big_step.outputEvent(new Event("entered_sc", "out", new Array()));
};

c.prototype._p_o1_sd_enter = function() {
    this.big_step.outputEvent(new Event("entered_sd", "out", new Array()));
};

c.prototype._p_o1_se_enter = function() {
    this.big_step.outputEvent(new Event("entered_se", "out", new Array()));
};

c.prototype._p_o1_sf_enter = function() {
    this.big_step.outputEvent(new Event("entered_sf", "out", new Array()));
};

c.prototype.initializeStatechart = function() {
    // enter default state
    var states = this.states["/p"].getEffectiveTargetStates();
    this.updateConfiguration(states);
    for (var state_idx in states) {
        if (!states.hasOwnProperty(state_idx)) continue;
        var state = states[state_idx]
        if (state.enter) {
            state.enter();
        }
    }
};

// add symbol 'c' to package 'orthogonal_take_one'
orthogonal_take_one.c = c;

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

// add symbol 'ObjectManager' to package 'orthogonal_take_one'
orthogonal_take_one.ObjectManager = ObjectManager;

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

// add symbol 'Controller' to package 'orthogonal_take_one'
orthogonal_take_one.Controller = Controller;

var InputEvent = function(name, port, parameters, time_offset) {
    this.name = name;
    this.port = port;
    this.parameters = parameters;
    this.time_offset = time_offset;
};

// add symbol 'InputEvent' to package 'orthogonal_take_one'
orthogonal_take_one.InputEvent = InputEvent;

var Test = function() {
};
Test.prototype.input_events = new Array();
Test.prototype.expected_events = [[new Event("entered_sa", "out", new Array()), new Event("entered_sd", "out", new Array())], [new Event("entered_sb", "out", new Array()), new Event("entered_se", "out", new Array())], [new Event("entered_sc", "out", new Array()), new Event("entered_sf", "out", new Array())]];

// add symbol 'Test' to package 'orthogonal_take_one'
orthogonal_take_one.Test = Test;
})();