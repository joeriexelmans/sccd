"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Tue Aug 09 09:35:56 2016

Model author: Glenn De Jonghe
Model name:   TestAfter
Model description:
Used for testing the AFTER event.
"""

from sccd.runtime.statecharts_core import *

# package "TestAfter"

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
        
        # state /composite
        self.states["/composite"] = State(1, self)
        
        # state /composite/state_1
        self.states["/composite/state_1"] = State(2, self)
        self.states["/composite/state_1"].setEnter(self._composite_state_1_enter)
        self.states["/composite/state_1"].setExit(self._composite_state_1_exit)
        
        # state /composite/state_2
        self.states["/composite/state_2"] = State(3, self)
        self.states["/composite/state_2"].setEnter(self._composite_state_2_enter)
        
        # state /composite/state_3
        self.states["/composite/state_3"] = State(4, self)
        self.states["/composite/state_3"].setEnter(self._composite_state_3_enter)
        
        # add children
        self.states[""].addChild(self.states["/composite"])
        self.states["/composite"].addChild(self.states["/composite/state_1"])
        self.states["/composite"].addChild(self.states["/composite/state_2"])
        self.states["/composite"].addChild(self.states["/composite/state_3"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/composite"]
        self.states["/composite"].default_state = self.states["/composite/state_1"]
        
        # transition /composite/state_1
        _composite_state_1_0 = Transition(self, self.states["/composite/state_1"], [self.states["/composite/state_2"]])
        _composite_state_1_0.setTrigger(Event("_0after"))
        self.states["/composite/state_1"].addTransition(_composite_state_1_0)
        _composite_state_1_1 = Transition(self, self.states["/composite/state_1"], [self.states["/composite/state_3"]])
        _composite_state_1_1.setTrigger(Event("_1after"))
        self.states["/composite/state_1"].addTransition(_composite_state_1_1)
    
    def _composite_state_1_enter(self):
        self.addTimer(0, 0.1)
        self.addTimer(1, 0.2)
    
    def _composite_state_1_exit(self):
        self.removeTimer(0)
        self.removeTimer(1)
    
    def _composite_state_2_enter(self):
        self.big_step.outputEvent(Event("in_state_2", "test_output", []))
    
    def _composite_state_3_enter(self):
        self.big_step.outputEvent(Event("in_state_3", "test_output", []))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/composite"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

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
    def __init__(self, keep_running = None, behind_schedule_callback = None):
        if keep_running == None: keep_running = True
        if behind_schedule_callback == None: behind_schedule_callback = None
        ThreadsControllerBase.__init__(self, ObjectManager(self), keep_running, behind_schedule_callback)
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
    input_events = []
    expected_events = [[Event("in_state_2", "test_output", [])]]