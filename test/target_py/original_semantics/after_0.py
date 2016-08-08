"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Mon Aug 08 09:49:24 2016

Model author: Yentl Van Tendeloo
Model name:   after_0
Model description:
Used for testing the AFTER(0) event---which should not block the deletion of the B instance.
"""

from sccd.runtime.statecharts_core import *

# package "after_0"

class A(RuntimeClassBase):
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
        A.user_defined_constructor(self)
    
    def user_defined_constructor(self):
        pass
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, self)
        
        # state /x
        self.states["/x"] = State(1, self)
        self.states["/x"].setEnter(self._x_enter)
        
        # state /ready
        self.states["/ready"] = State(2, self)
        self.states["/ready"].setEnter(self._ready_enter)
        
        # state /done
        self.states["/done"] = State(3, self)
        
        # add children
        self.states[""].addChild(self.states["/x"])
        self.states[""].addChild(self.states["/ready"])
        self.states[""].addChild(self.states["/done"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/x"]
        
        # transition /x
        _x_0 = Transition(self, self.states["/x"], [self.states["/ready"]])
        _x_0.setTrigger(Event("instance_created", None))
        self.states["/x"].addTransition(_x_0)
        
        # transition /ready
        _ready_0 = Transition(self, self.states["/ready"], [self.states["/done"]])
        _ready_0.setAction(self._ready_0_exec)
        _ready_0.setTrigger(Event("close", None))
        self.states["/ready"].addTransition(_ready_0)
    
    def _x_enter(self):
        self.big_step.outputEventOM(Event("create_instance", None, [self, 'child', 'B']))
        self.big_step.outputEvent(Event("creating_instance", "test_output", []))
    
    def _ready_enter(self):
        self.big_step.outputEventOM(Event("start_instance", None, [self, 'child[0]']))
        self.big_step.outputEvent(Event("starting_instance", "test_output", []))
    
    def _ready_0_exec(self, parameters):
        self.big_step.outputEventOM(Event("delete_instance", None, [self, 'child[0]']))
        self.big_step.outputEvent(Event("deleting_instance", "test_output", []))
    
    def initializeStatechart(self):
        # enter default state
        states = self.states["/x"].getEffectiveTargetStates()
        self.updateConfiguration(states)
        for state in states:
            if state.enter:
                state.enter()

class B(RuntimeClassBase):
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
        B.user_defined_constructor(self)
    
    def user_defined_constructor(self):
        pass
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, self)
        
        # state /z
        self.states["/z"] = State(1, self)
        self.states["/z"].setEnter(self._z_enter)
        self.states["/z"].setExit(self._z_exit)
        
        # add children
        self.states[""].addChild(self.states["/z"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/z"]
        
        # transition /z
        _z_0 = Transition(self, self.states["/z"], [self.states["/z"]])
        _z_0.setAction(self._z_0_exec)
        _z_0.setTrigger(Event("_0after"))
        self.states["/z"].addTransition(_z_0)
    
    def _z_enter(self):
        self.addTimer(0, 0)
    
    def _z_exit(self):
        self.removeTimer(0)
    
    def _z_0_exec(self, parameters):
        self.big_step.outputEventOM(Event("broad_cast", None, [Event("close", None, [])]))
        self.big_step.outputEvent(Event("after_0", "test_output", []))
    
    def initializeStatechart(self):
        # enter default state
        states = self.states["/z"].getEffectiveTargetStates()
        self.updateConfiguration(states)
        for state in states:
            if state.enter:
                state.enter()

class ObjectManager(ObjectManagerBase):
    def __init__(self, controller):
        ObjectManagerBase.__init__(self, controller)
    
    def instantiate(self, class_name, construct_params):
        if class_name == "A":
            instance = A(self.controller)
            instance.associations = {}
            instance.associations["child"] = Association("B", 0, 1)
        elif class_name == "B":
            instance = B(self.controller)
            instance.associations = {}
            instance.associations["parent"] = Association("A", 1, 1)
        else:
            raise Exception("Cannot instantiate class " + class_name)
        return instance

class Controller(ThreadsControllerBase):
    def __init__(self, keep_running = None):
        if keep_running == None: keep_running = True
        ThreadsControllerBase.__init__(self, ObjectManager(self), keep_running)
        self.addOutputPort("test_output")
        self.object_manager.createInstance("A", [])

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
    expected_events = [[Event("creating_instance", "test_output", [])], [Event("starting_instance", "test_output", [])], [Event("after_0", "test_output", [])], [Event("deleting_instance", "test_output", []), Event("after_0", "test_output", [])]]