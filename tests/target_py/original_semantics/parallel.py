"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Wed Aug 03 16:10:24 2016

Model author: Glenn De Jonghe
Model name:   TestParallel
Model description:
Testing parallelism.
"""

from python_runtime.statecharts_core import *

# package "TestParallel"

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
        
        # state /parallel_1
        self.states["/parallel_1"] = ParallelState(1, self)
        
        # state /parallel_1/orthogonal_1
        self.states["/parallel_1/orthogonal_1"] = State(2, self)
        
        # state /parallel_1/orthogonal_1/state_1
        self.states["/parallel_1/orthogonal_1/state_1"] = State(3, self)
        self.states["/parallel_1/orthogonal_1/state_1"].setEnter(self._parallel_1_orthogonal_1_state_1_enter)
        
        # state /parallel_1/orthogonal_1/state_2
        self.states["/parallel_1/orthogonal_1/state_2"] = State(4, self)
        self.states["/parallel_1/orthogonal_1/state_2"].setEnter(self._parallel_1_orthogonal_1_state_2_enter)
        
        # state /parallel_1/orthogonal_2
        self.states["/parallel_1/orthogonal_2"] = State(5, self)
        
        # state /parallel_1/orthogonal_2/state_3
        self.states["/parallel_1/orthogonal_2/state_3"] = State(6, self)
        self.states["/parallel_1/orthogonal_2/state_3"].setEnter(self._parallel_1_orthogonal_2_state_3_enter)
        
        # state /parallel_1/orthogonal_2/state_4
        self.states["/parallel_1/orthogonal_2/state_4"] = State(7, self)
        self.states["/parallel_1/orthogonal_2/state_4"].setEnter(self._parallel_1_orthogonal_2_state_4_enter)
        
        # add children
        self.states[""].addChild(self.states["/parallel_1"])
        self.states["/parallel_1"].addChild(self.states["/parallel_1/orthogonal_1"])
        self.states["/parallel_1"].addChild(self.states["/parallel_1/orthogonal_2"])
        self.states["/parallel_1/orthogonal_1"].addChild(self.states["/parallel_1/orthogonal_1/state_1"])
        self.states["/parallel_1/orthogonal_1"].addChild(self.states["/parallel_1/orthogonal_1/state_2"])
        self.states["/parallel_1/orthogonal_2"].addChild(self.states["/parallel_1/orthogonal_2/state_3"])
        self.states["/parallel_1/orthogonal_2"].addChild(self.states["/parallel_1/orthogonal_2/state_4"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/parallel_1"]
        self.states["/parallel_1/orthogonal_1"].default_state = self.states["/parallel_1/orthogonal_1/state_1"]
        self.states["/parallel_1/orthogonal_2"].default_state = self.states["/parallel_1/orthogonal_2/state_3"]
        
        # transition /parallel_1/orthogonal_1/state_1
        _parallel_1_orthogonal_1_state_1_0 = Transition(self, self.states["/parallel_1/orthogonal_1/state_1"], [self.states["/parallel_1/orthogonal_1/state_2"]])
        _parallel_1_orthogonal_1_state_1_0.trigger = Event("to_state_2", "test_input")
        self.states["/parallel_1/orthogonal_1/state_1"].addTransition(_parallel_1_orthogonal_1_state_1_0)
        
        # transition /parallel_1/orthogonal_1/state_2
        _parallel_1_orthogonal_1_state_2_0 = Transition(self, self.states["/parallel_1/orthogonal_1/state_2"], [self.states["/parallel_1/orthogonal_1/state_1"]])
        _parallel_1_orthogonal_1_state_2_0.trigger = Event("to_state_1", "test_input")
        self.states["/parallel_1/orthogonal_1/state_2"].addTransition(_parallel_1_orthogonal_1_state_2_0)
        
        # transition /parallel_1/orthogonal_2/state_3
        _parallel_1_orthogonal_2_state_3_0 = Transition(self, self.states["/parallel_1/orthogonal_2/state_3"], [self.states["/parallel_1/orthogonal_2/state_4"]])
        _parallel_1_orthogonal_2_state_3_0.trigger = Event("to_state_4", "test_input")
        self.states["/parallel_1/orthogonal_2/state_3"].addTransition(_parallel_1_orthogonal_2_state_3_0)
        
        # transition /parallel_1/orthogonal_2/state_4
        _parallel_1_orthogonal_2_state_4_0 = Transition(self, self.states["/parallel_1/orthogonal_2/state_4"], [self.states["/parallel_1/orthogonal_2/state_3"]])
        _parallel_1_orthogonal_2_state_4_0.trigger = Event("to_state_3", "test_input")
        self.states["/parallel_1/orthogonal_2/state_4"].addTransition(_parallel_1_orthogonal_2_state_4_0)
    
    def _parallel_1_orthogonal_1_state_1_enter(self):
        self.big_step.outputEvent(Event("in_state_1", "test_output", []))
    
    def _parallel_1_orthogonal_1_state_2_enter(self):
        self.big_step.outputEvent(Event("in_state_2", "test_output", []))
    
    def _parallel_1_orthogonal_2_state_3_enter(self):
        self.big_step.outputEvent(Event("in_state_3", "test_output", []))
    
    def _parallel_1_orthogonal_2_state_4_enter(self):
        self.big_step.outputEvent(Event("in_state_4", "test_output", []))
    
    def initializeStatechart(self):
        # enter default state
        states = self.states["/parallel_1"].getEffectiveTargetStates()
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
    input_events = [InputEvent("to_state_2", "test_input", [], 0.0), InputEvent("to_state_4", "test_input", [], 0.0), InputEvent("to_state_1", "test_input", [], 0.0), InputEvent("to_state_2", "test_input", [], 0.0), InputEvent("to_state_3", "test_input", [], 0.0)]
    expected_events = [[Event("in_state_1", "test_output", []), Event("in_state_3", "test_output", [])], [Event("in_state_2", "test_output", [])], [Event("in_state_4", "test_output", [])], [Event("in_state_1", "test_output", [])], [Event("in_state_2", "test_output", [])], [Event("in_state_3", "test_output", [])]]