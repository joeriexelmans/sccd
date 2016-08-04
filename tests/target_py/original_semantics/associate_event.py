"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Wed Aug 03 16:10:23 2016

Model author: Glenn De Jonghe
Model name:   TestAssociateEvent
Model description:
Testing the object manager
"""

from python_runtime.statecharts_core import *

# package "TestAssociateEvent"

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
        
        # state /start
        self.states["/start"] = State(1, self)
        
        # state /wait
        self.states["/wait"] = State(2, self)
        
        # add children
        self.states[""].addChild(self.states["/start"])
        self.states[""].addChild(self.states["/wait"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/start"]
        
        # transition /start
        _start_0 = Transition(self, self.states["/start"], [self.states["/wait"]])
        _start_0.setAction(self._start_0_exec)
        _start_0.trigger = Event("create", "test_input")
        self.states["/start"].addTransition(_start_0)
        
        # transition /wait
        _wait_0 = Transition(self, self.states["/wait"], [self.states["/start"]])
        _wait_0.setAction(self._wait_0_exec)
        _wait_0.trigger = Event("instance_created", None)
        self.states["/wait"].addTransition(_wait_0)
    
    def _start_0_exec(self, parameters):
        self.big_step.outputEventOM(Event("create_instance", None, [self, "test2_association"]))
        self.big_step.outputEvent(Event("request_send", "test_output", []))
    
    def _wait_0_exec(self, parameters):
        association_name = parameters[0]
        self.big_step.outputEvent(Event("instance_created", "test_output", []))
        self.big_step.outputEventOM(Event("start_instance", None, [self, "test2_association"]))
        self.big_step.outputEventOM(Event("narrow_cast", None, [self, "test2_association", Event("hello", None, [])]))
        self.big_step.outputEventOM(Event("associate_instance", None, [self, "test2_association", "test3_association"]))
    
    def initializeStatechart(self):
        # enter default state
        states = self.states["/start"].getEffectiveTargetStates()
        self.updateConfiguration(states)
        for state in states:
            if state.enter:
                state.enter()

class Class2(RuntimeClassBase):
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
        Class2.user_defined_constructor(self)
    
    def user_defined_constructor(self):
        pass
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, self)
        
        # state /start
        self.states["/start"] = State(1, self)
        
        # add children
        self.states[""].addChild(self.states["/start"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/start"]
        
        # transition /start
        _start_0 = Transition(self, self.states["/start"], [self.states["/start"]])
        _start_0.setAction(self._start_0_exec)
        _start_0.trigger = Event("hello", None)
        self.states["/start"].addTransition(_start_0)
    
    def _start_0_exec(self, parameters):
        self.big_step.outputEvent(Event("second_working", "test_output", []))
    
    def initializeStatechart(self):
        # enter default state
        states = self.states["/start"].getEffectiveTargetStates()
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
            instance.associations["test2_association"] = Association("Class2", 0, -1)
            instance.associations["test3_association"] = Association("Class2", 0, -1)
        elif class_name == "Class2":
            instance = Class2(self.controller)
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
    input_events = [InputEvent("create", "test_input", [], 0.0)]
    expected_events = [[Event("request_send", "test_output", [])], [Event("instance_created", "test_output", [])], [Event("second_working", "test_output", [])]]