/* Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Wed Aug 03 16:58:36 2016

Model author: Simon Van Mierlo
Model name:   Timer
*/


// package "Timer"
var Timer = {};
(function() {

var MainApp = function(controller) {
    RuntimeClassBase.call(this, controller);
    
    this.semantics.big_step_maximality = StatechartSemantics.TakeMany;
    this.semantics.internal_event_lifeline = StatechartSemantics.Queue;
    this.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep;
    this.semantics.priority = StatechartSemantics.SourceParent;
    this.semantics.concurrency = StatechartSemantics.Single;
    
    // build Statechart structure
    this.build_statechart_structure();
    
    // call user defined constructor
    MainApp.prototype.user_defined_constructor.call(this);
};
MainApp.prototype = new Object();
(function() {
    var proto = new RuntimeClassBase();
    for (prop in proto) {
        MainApp.prototype[prop] = proto[prop];
    }
})();

MainApp.prototype.user_defined_constructor = function() {
    this.canvas = ui.append_canvas(ui.window,400,150,{'background':'#eee'})
    this.clock_text = this.canvas.add_text(25,25,'0.0')
    this.actual_clock_text = this.canvas.add_text(25,50,'0.0')
    var interrupt_button = ui.append_button(ui.window, 'INTERRUPT');
    var continue_button = ui.append_button(ui.window, 'CONTINUE');
    ui.bind_event(interrupt_button.element, ui.EVENTS.MOUSE_CLICK, this.controller, 'interrupt_clicked');
    ui.bind_event(continue_button.element, ui.EVENTS.MOUSE_CLICK, this.controller, 'continue_clicked');
};

MainApp.prototype.user_defined_destructor = function() {
};


// user defined method
MainApp.prototype.update_timers = function() {
    this.clock_text.set_text(get_simulated_time().toFixed(2));
    this.actual_clock_text.set_text(time().toFixed(2));
};


// builds Statechart structure
MainApp.prototype.build_statechart_structure = function() {
    
    // state <root>
    this.states[""] = new State(0, this);
    
    // state /running
    this.states["/running"] = new State(1, this);
    this.states["/running"].setEnter(this._running_enter);
    this.states["/running"].setExit(this._running_exit);
    
    // state /interrupted
    this.states["/interrupted"] = new State(2, this);
    this.states["/interrupted"].setEnter(this._interrupted_enter);
    this.states["/interrupted"].setExit(this._interrupted_exit);
    
    // add children
    this.states[""].addChild(this.states["/running"]);
    this.states[""].addChild(this.states["/interrupted"]);
    this.states[""].fixTree();
    this.states[""].default_state = this.states["/running"];
    
    // transition /running
    var _running_0 = new Transition(this, this.states["/running"], [this.states["/running"]]);
    _running_0.setAction(this._running_0_exec);
    _running_0.trigger = new Event("_0after");
    this.states["/running"].addTransition(_running_0);
    var _running_1 = new Transition(this, this.states["/running"], [this.states["/interrupted"]]);
    _running_1.setAction(this._running_1_exec);
    _running_1.trigger = new Event("interrupt_clicked", "ui");
    this.states["/running"].addTransition(_running_1);
    
    // transition /interrupted
    var _interrupted_0 = new Transition(this, this.states["/interrupted"], [this.states["/interrupted"]]);
    _interrupted_0.setAction(this._interrupted_0_exec);
    _interrupted_0.trigger = new Event("interrupt_clicked", "ui");
    this.states["/interrupted"].addTransition(_interrupted_0);
    var _interrupted_1 = new Transition(this, this.states["/interrupted"], [this.states["/running"]]);
    _interrupted_1.setAction(this._interrupted_1_exec);
    _interrupted_1.trigger = new Event("continue_clicked", "ui");
    this.states["/interrupted"].addTransition(_interrupted_1);
};

MainApp.prototype._running_enter = function() {
    this.addTimer(0, 0.05);
};

MainApp.prototype._running_exit = function() {
    this.removeTimer(0);
};

MainApp.prototype._interrupted_enter = function() {
    console.log("entering interrupted");
};

MainApp.prototype._interrupted_exit = function() {
    console.log("entering interrupted");
};

MainApp.prototype._running_0_exec = function(parameters) {
    this.update_timers();
};

MainApp.prototype._running_1_exec = function(parameters) {
    this.update_timers();
};

MainApp.prototype._interrupted_0_exec = function(parameters) {
    this.update_timers();
};

MainApp.prototype._interrupted_1_exec = function(parameters) {
    this.update_timers();
};

MainApp.prototype.initializeStatechart = function() {
    // enter default state
    var states = this.states["/running"].getEffectiveTargetStates();
    this.updateConfiguration(states);
    for (var state_idx in states) {
        if (!states.hasOwnProperty(state_idx)) continue;
        var state = states[state_idx]
        if (state.enter) {
            state.enter();
        }
    }
};

// add symbol 'MainApp' to package 'Timer'
Timer.MainApp = MainApp;

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
    if (class_name === "MainApp") {
        var instance = new MainApp(this.controller);
        instance.associations = new Object();
    }
    return instance;
};

// add symbol 'ObjectManager' to package 'Timer'
Timer.ObjectManager = ObjectManager;

var Controller = function(event_loop_callbacks, finished_callback) {
    if (finished_callback === undefined) finished_callback = null;
    EventLoopControllerBase.call(this, new ObjectManager(this), event_loop_callbacks, finished_callback);
    this.addInputPort("ui");
    this.object_manager.createInstance("MainApp", new Array());
};
Controller.prototype = new Object();
(function() {
    var proto = new EventLoopControllerBase();
    for (prop in proto) {
        Controller.prototype[prop] = proto[prop];
    }
})();

// add symbol 'Controller' to package 'Timer'
Timer.Controller = Controller;
})();