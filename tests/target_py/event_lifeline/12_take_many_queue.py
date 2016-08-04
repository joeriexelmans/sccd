"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Wed Aug 03 16:10:22 2016

Model author: Herr Joeri Exelmans
Model name:   take_many_queue
Model description:
Internal event lifeline - Queue-semantics: Internally raised events are treated like external events and are added to the object's event queue. They become present in another big step later on.
"""

from python_runtime.statecharts_core import *

# package "take_many_queue"

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
        
        # call user defined constructor
        c.user_defined_constructor(self)
    
    def user_defined_constructor(self):
        pass
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, self)
        
        # state /a
        self.states["/a"] = State(1, self)
        self.states["/a"].setEnter(self._a_enter)
        
        # state /b
        self.states["/b"] = State(2, self)
        self.states["/b"].setEnter(self._b_enter)
        
        # state /c
        self.states["/c"] = State(3, self)
        self.states["/c"].setEnter(self._c_enter)
        
        # add children
        self.states[""].addChild(self.states["/a"])
        self.states[""].addChild(self.states["/b"])
        self.states[""].addChild(self.states["/c"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/a"]
        
        # transition /a
        _a_0 = Transition(self, self.states["/a"], [self.states["/b"]])
        _a_0.setAction(self._a_0_exec)
        _a_0.trigger = Event("e", "in")
        self.states["/a"].addTransition(_a_0)
        
        # transition /b
        _b_0 = Transition(self, self.states["/b"], [self.states["/c"]])
        _b_0.trigger = Event("f", None)
        self.states["/b"].addTransition(_b_0)
    
    def _a_enter(self):
        self.big_step.outputEvent(Event("entered_a", "out", []))
    
    def _b_enter(self):
        self.big_step.outputEvent(Event("entered_b", "out", []))
    
    def _c_enter(self):
        self.big_step.outputEvent(Event("entered_c", "out", []))
    
    def _a_0_exec(self, parameters):
        self.raiseInternalEvent(Event("f", None, []))
    
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
    input_events = [InputEvent("e", "in", [], 0.0)]
    expected_events = [[Event("entered_a", "out", [])], [Event("entered_b", "out", [])], [Event("entered_c", "out", [])]]