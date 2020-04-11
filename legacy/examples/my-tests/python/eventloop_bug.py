"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Wed Sep 27 15:08:22 2017

Model name:   multiple-raises-parallel

"""

from sccd.runtime.statecharts_core import *

# package "multiple-raises-parallel"

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
        self.states[""] = State(0, "", self)
        
        # state /listening
        self.states["/listening"] = State(1, "/listening", self)
        self.states["/listening"].setEnter(self._listening_enter)
        self.states["/listening"].setExit(self._listening_exit)
        
        # add children
        self.states[""].addChild(self.states["/listening"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/listening"]
        
        # transition /listening
        _listening_0 = Transition(self, self.states["/listening"], [self.states["/listening"]])
        _listening_0.setAction(self._listening_0_exec)
        _listening_0.setTrigger(Event("input", "input"))
        self.states["/listening"].addTransition(_listening_0)
        _listening_1 = Transition(self, self.states["/listening"], [self.states["/listening"]])
        _listening_1.setTrigger(Event("_0after"))
        self.states["/listening"].addTransition(_listening_1)
    
    def _listening_enter(self):
        self.addTimer(0, 1)
    
    def _listening_exit(self):
        self.removeTimer(0)
    
    def _listening_0_exec(self, parameters):
        value = parameters[0]
        print(value)
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/listening"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class ObjectManager(ObjectManagerBase):
    def __init__(self, controller):
        ObjectManagerBase.__init__(self, controller)
    
    def instantiate(self, class_name, construct_params):
        if class_name == "A":
            instance = A(self.controller)
            instance.associations = {}
        else:
            raise Exception("Cannot instantiate class " + class_name)
        return instance

class Controller(EventLoopControllerBase):
    def __init__(self, event_loop_callbacks, finished_callback = None, behind_schedule_callback = None):
        if finished_callback == None: finished_callback = None
        if behind_schedule_callback == None: behind_schedule_callback = None
        EventLoopControllerBase.__init__(self, ObjectManager(self), event_loop_callbacks, finished_callback, behind_schedule_callback)
        self.addInputPort("input")
        self.object_manager.createInstance("A", [])