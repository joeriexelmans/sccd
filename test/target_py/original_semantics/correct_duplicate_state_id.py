"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Fri Aug 05 16:13:33 2016

Model author: Glenn De Jonghe
Model name:   TestCorrectDuplicateStateId
Model description:
Testing duplicate id's.
"""

from sccd.runtime.statecharts_core import *

# package "TestCorrectDuplicateStateId"

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
        
        # state /state0
        self.states["/state0"] = State(1, self)
        
        # state /state0/state1
        self.states["/state0/state1"] = State(2, self)
        
        # state /state0/state0
        self.states["/state0/state0"] = State(3, self)
        
        # state /state1
        self.states["/state1"] = State(4, self)
        
        # state /state1/state1
        self.states["/state1/state1"] = State(5, self)
        
        # state /state1/state0
        self.states["/state1/state0"] = State(6, self)
        
        # add children
        self.states[""].addChild(self.states["/state0"])
        self.states[""].addChild(self.states["/state1"])
        self.states["/state0"].addChild(self.states["/state0/state1"])
        self.states["/state0"].addChild(self.states["/state0/state0"])
        self.states["/state1"].addChild(self.states["/state1/state1"])
        self.states["/state1"].addChild(self.states["/state1/state0"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/state1"]
        self.states["/state0"].default_state = self.states["/state0/state1"]
        self.states["/state1"].default_state = self.states["/state1/state1"]
    
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
    input_events = []
    expected_events = []