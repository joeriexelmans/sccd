"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Wed Aug 03 16:10:25 2016

Model author: Herr Joeri Exelmans
Model name:   rapid
Model description:
After event with a very small timeout.
"""

from python_runtime.statecharts_core import *

# package "rapid"

class c(RuntimeClassBase):
    def __init__(self, controller):
        RuntimeClassBase.__init__(self, controller)
        
        self.semantics.big_step_maximality = StatechartSemantics.TakeMany
        self.semantics.internal_event_lifeline = StatechartSemantics.Queue
        self.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep
        self.semantics.priority = StatechartSemantics.SourceParent
        self.semantics.concurrency = StatechartSemantics.Single
        
        # build Statechart structure
        self.build_statechart_structure()
        
        # user defined attributes
        self.i = None
        
        # call user defined constructor
        c.user_defined_constructor(self)
    
    def user_defined_constructor(self):
        self.i = 0
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, self)
        
        # state /a
        self.states["/a"] = State(1, self)
        self.states["/a"].setEnter(self._a_enter)
        self.states["/a"].setExit(self._a_exit)
        
        # add children
        self.states[""].addChild(self.states["/a"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/a"]
        
        # transition /a
        _a_0 = Transition(self, self.states["/a"], [self.states["/a"]])
        _a_0.setAction(self._a_0_exec)
        _a_0.trigger = Event("_0after")
        _a_0.setGuard(self._a_0_guard)
        self.states["/a"].addTransition(_a_0)
    
    def _a_enter(self):
        self.addTimer(0, 1e-10)
        self.big_step.outputEvent(Event("entered_a", "out", []))
    
    def _a_exit(self):
        self.removeTimer(0)
    
    def _a_0_exec(self, parameters):
        self.i += 1
    
    def _a_0_guard(self, parameters):
        return self.i < 2
    
    def initializeStatechart(self):
        # enter default state
        states = self.states["/a"].getEffectiveTargetStates()
        self.updateConfiguration(states)
        for state in states:
            if state.enter:
                state.enter()

class ObjectManager(ObjectManagerBase):
    def __init__(self, controller):
        ObjectManagerBase.__init__(self, controller)
    
    def instantiate(self, class_name, construct_params):
        if class_name == "c":
            instance = c(self.controller)
            instance.associations = {}
        return instance

class Controller(ThreadsControllerBase):
    def __init__(self, keep_running = None):
        if keep_running == None: keep_running = True
        ThreadsControllerBase.__init__(self, ObjectManager(self), keep_running)
        self.addInputPort("in")
        self.addOutputPort("out")
        self.object_manager.createInstance("c", [])

class InputEvent:
    def __init__(self, name, port, parameters, time_offset):
        self.name = name
        self.port = port
        self.parameters = parameters
        self.time_offset = time_offset

class Test:
    def __init__(self):
        pass
    input_events = []
    expected_events = [[Event("entered_a", "out", [])], [Event("entered_a", "out", [])], [Event("entered_a", "out", [])]]