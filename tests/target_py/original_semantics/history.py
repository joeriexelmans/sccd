"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Wed Aug 03 16:10:23 2016

Model author: Glenn De Jonghe
Model name:   TestHistory
Model description:
Testing the History state.
"""

from python_runtime.statecharts_core import *

# package "TestHistory"

class Class1(RuntimeClassBase):
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
        Class1.user_defined_constructor(self)
    
    def user_defined_constructor(self):
        pass
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, self)
        
        # state /composite_1
        self.states["/composite_1"] = State(1, self)
        
        # state /composite_1/state_1
        self.states["/composite_1/state_1"] = State(2, self)
        self.states["/composite_1/state_1"].setEnter(self._composite_1_state_1_enter)
        
        # state /composite_1/state_2
        self.states["/composite_1/state_2"] = State(3, self)
        self.states["/composite_1/state_2"].setEnter(self._composite_1_state_2_enter)
        
        # state /composite_1/composite_history
        self.states["/composite_1/composite_history"] = ShallowHistoryState(4, self)
        
        # state /state_3
        self.states["/state_3"] = State(5, self)
        self.states["/state_3"].setEnter(self._state_3_enter)
        
        # add children
        self.states[""].addChild(self.states["/composite_1"])
        self.states[""].addChild(self.states["/state_3"])
        self.states["/composite_1"].addChild(self.states["/composite_1/state_1"])
        self.states["/composite_1"].addChild(self.states["/composite_1/state_2"])
        self.states["/composite_1"].addChild(self.states["/composite_1/composite_history"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/composite_1"]
        self.states["/composite_1"].default_state = self.states["/composite_1/state_1"]
        
        # transition /composite_1/state_1
        _composite_1_state_1_0 = Transition(self, self.states["/composite_1/state_1"], [self.states["/composite_1/state_2"]])
        _composite_1_state_1_0.trigger = Event("to_state_2", "test_input")
        self.states["/composite_1/state_1"].addTransition(_composite_1_state_1_0)
        
        # transition /state_3
        _state_3_0 = Transition(self, self.states["/state_3"], [self.states["/composite_1/composite_history"]])
        self.states["/state_3"].addTransition(_state_3_0)
        
        # transition /composite_1
        _composite_1_0 = Transition(self, self.states["/composite_1"], [self.states["/state_3"]])
        _composite_1_0.trigger = Event("to_state_3", "test_input")
        self.states["/composite_1"].addTransition(_composite_1_0)
    
    def _composite_1_state_1_enter(self):
        self.big_step.outputEvent(Event("in_state_1", "test_output", []))
    
    def _composite_1_state_2_enter(self):
        self.big_step.outputEvent(Event("in_state_2", "test_output", []))
    
    def _state_3_enter(self):
        self.big_step.outputEvent(Event("in_state_3", "test_output", []))
    
    def initializeStatechart(self):
        # enter default state
        states = self.states["/composite_1"].getEffectiveTargetStates()
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
    input_events = [InputEvent("to_state_2", "test_input", [], 0.0), InputEvent("to_state_3", "test_input", [], 0.0)]
    expected_events = [[Event("in_state_1", "test_output", [])], [Event("in_state_2", "test_output", [])], [Event("in_state_3", "test_output", [])], [Event("in_state_2", "test_output", [])]]