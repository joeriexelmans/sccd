"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Mon Aug 08 09:49:25 2016

Model author: Glenn De Jonghe
Model name:   TestInnerFirst
Model description:
Testing inner first.
"""

from sccd.runtime.statecharts_core import *

# package "TestInnerFirst"

class Class1(RuntimeClassBase):
    def __init__(self, controller):
        RuntimeClassBase.__init__(self, controller)
        
        self.semantics.big_step_maximality = StatechartSemantics.TakeMany
        self.semantics.internal_event_lifeline = StatechartSemantics.Queue
        self.semantics.input_event_lifeline = StatechartSemantics.FirstComboStep
        self.semantics.priority = StatechartSemantics.SourceChild
        self.semantics.concurrency = StatechartSemantics.Single
        
        # build Statechart structure
        self.build_statechart_structure()
        
        # call user defined constructor
        Class1.user_defined_constructor(self)
    
    def user_defined_constructor(self):
        pass
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, self)
        
        # state /state1
        self.states["/state1"] = State(1, self)
        
        # state /state1/state1
        self.states["/state1/state1"] = State(2, self)
        
        # state /state1/statea
        self.states["/state1/statea"] = State(3, self)
        self.states["/state1/statea"].setEnter(self._state1_statea_enter)
        
        # state /stateb
        self.states["/stateb"] = State(4, self)
        self.states["/stateb"].setEnter(self._stateb_enter)
        
        # add children
        self.states[""].addChild(self.states["/state1"])
        self.states[""].addChild(self.states["/stateb"])
        self.states["/state1"].addChild(self.states["/state1/state1"])
        self.states["/state1"].addChild(self.states["/state1/statea"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/state1"]
        self.states["/state1"].default_state = self.states["/state1/state1"]
        
        # transition /state1/state1
        _state1_state1_0 = Transition(self, self.states["/state1/state1"], [self.states["/state1/statea"]])
        _state1_state1_0.setTrigger(Event("event", "test_input"))
        self.states["/state1/state1"].addTransition(_state1_state1_0)
        
        # transition /state1
        _state1_0 = Transition(self, self.states["/state1"], [self.states["/stateb"]])
        _state1_0.setTrigger(Event("event", "test_input"))
        self.states["/state1"].addTransition(_state1_0)
    
    def _state1_statea_enter(self):
        self.big_step.outputEvent(Event("in_a", "test_output", []))
    
    def _stateb_enter(self):
        self.big_step.outputEvent(Event("in_b", "test_output", []))
    
    def initializeStatechart(self):
        # enter default state
        states = self.states["/state1"].getEffectiveTargetStates()
        self.updateConfiguration(states)
        for state in states:
            if state.enter:
                state.enter()

class ObjectManager(ObjectManagerBase):
    def __init__(self, controller):
        ObjectManagerBase.__init__(self, controller)
    
    def instantiate(self, class_name, construct_params):
        if class_name == "Class1":
            instance = Class1(self.controller)
            instance.associations = {}
        else:
            raise Exception("Cannot instantiate class " + class_name)
        return instance

class Controller(ThreadsControllerBase):
    def __init__(self, keep_running = None):
        if keep_running == None: keep_running = True
        ThreadsControllerBase.__init__(self, ObjectManager(self), keep_running)
        self.addInputPort("test_input")
        self.addOutputPort("test_output")
        self.object_manager.createInstance("Class1", [])

class InputEvent:
    def __init__(self, name, port, parameters, time_offset):
        self.name = name
        self.port = port
        self.parameters = parameters
        self.time_offset = time_offset

class Test:
    def __init__(self):
        pass
    input_events = [InputEvent("event", "test_input", [], 0.0)]
    expected_events = [[Event("in_a", "test_output", [])]]