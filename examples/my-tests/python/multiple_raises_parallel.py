"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Fri Jul 28 15:14:50 2017

Model name:   multiple-raises-parallel

"""

from sccd.runtime.statecharts_core import *

# package "multiple-raises-parallel"

class A(RuntimeClassBase):
    def __init__(self, controller):
        RuntimeClassBase.__init__(self, controller)
        
        self.semantics.big_step_maximality = StatechartSemantics.TakeOne
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
        
        # state /x
        self.states["/x"] = ParallelState(1, "/x", self)
        
        # state /x/x1
        self.states["/x/x1"] = State(2, "/x/x1", self)
        
        # state /x/x1/x1
        self.states["/x/x1/x1"] = State(3, "/x/x1/x1", self)
        
        # state /x/x1/end
        self.states["/x/x1/end"] = State(4, "/x/x1/end", self)
        
        # state /x/x2
        self.states["/x/x2"] = State(5, "/x/x2", self)
        
        # state /x/x2/x2
        self.states["/x/x2/x2"] = State(6, "/x/x2/x2", self)
        
        # state /x/x2/end
        self.states["/x/x2/end"] = State(7, "/x/x2/end", self)
        
        # state /x/x3
        self.states["/x/x3"] = State(8, "/x/x3", self)
        
        # state /x/x3/x3
        self.states["/x/x3/x3"] = State(9, "/x/x3/x3", self)
        
        # state /x/x3/end
        self.states["/x/x3/end"] = State(10, "/x/x3/end", self)
        
        # state /x/receiving
        self.states["/x/receiving"] = State(11, "/x/receiving", self)
        
        # state /x/receiving/receiving
        self.states["/x/receiving/receiving"] = State(12, "/x/receiving/receiving", self)
        
        # add children
        self.states[""].addChild(self.states["/x"])
        self.states["/x"].addChild(self.states["/x/x1"])
        self.states["/x"].addChild(self.states["/x/x2"])
        self.states["/x"].addChild(self.states["/x/x3"])
        self.states["/x"].addChild(self.states["/x/receiving"])
        self.states["/x/x1"].addChild(self.states["/x/x1/x1"])
        self.states["/x/x1"].addChild(self.states["/x/x1/end"])
        self.states["/x/x2"].addChild(self.states["/x/x2/x2"])
        self.states["/x/x2"].addChild(self.states["/x/x2/end"])
        self.states["/x/x3"].addChild(self.states["/x/x3/x3"])
        self.states["/x/x3"].addChild(self.states["/x/x3/end"])
        self.states["/x/receiving"].addChild(self.states["/x/receiving/receiving"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/x"]
        self.states["/x/x1"].default_state = self.states["/x/x1/x1"]
        self.states["/x/x2"].default_state = self.states["/x/x2/x2"]
        self.states["/x/x3"].default_state = self.states["/x/x3/x3"]
        self.states["/x/receiving"].default_state = self.states["/x/receiving/receiving"]
        
        # transition /x/x1/x1
        _x_x1_x1_0 = Transition(self, self.states["/x/x1/x1"], [self.states["/x/x1/end"]])
        _x_x1_x1_0.setAction(self._x_x1_x1_0_exec)
        _x_x1_x1_0.setTrigger(None)
        self.states["/x/x1/x1"].addTransition(_x_x1_x1_0)
        
        # transition /x/x2/x2
        _x_x2_x2_0 = Transition(self, self.states["/x/x2/x2"], [self.states["/x/x2/end"]])
        _x_x2_x2_0.setAction(self._x_x2_x2_0_exec)
        _x_x2_x2_0.setTrigger(None)
        self.states["/x/x2/x2"].addTransition(_x_x2_x2_0)
        
        # transition /x/x3/x3
        _x_x3_x3_0 = Transition(self, self.states["/x/x3/x3"], [self.states["/x/x3/end"]])
        _x_x3_x3_0.setAction(self._x_x3_x3_0_exec)
        _x_x3_x3_0.setTrigger(None)
        self.states["/x/x3/x3"].addTransition(_x_x3_x3_0)
        
        # transition /x/receiving/receiving
        _x_receiving_receiving_0 = Transition(self, self.states["/x/receiving/receiving"], [self.states["/x/receiving/receiving"]])
        _x_receiving_receiving_0.setAction(self._x_receiving_receiving_0_exec)
        _x_receiving_receiving_0.setTrigger(Event("z", None))
        self.states["/x/receiving/receiving"].addTransition(_x_receiving_receiving_0)
    
    def _x_x1_x1_0_exec(self, parameters):
        self.raiseInternalEvent(Event("z", None, []))
        print 'raised event in x1'
    
    def _x_x2_x2_0_exec(self, parameters):
        self.raiseInternalEvent(Event("z", None, []))
        print 'raised event in x2'
    
    def _x_x3_x3_0_exec(self, parameters):
        self.raiseInternalEvent(Event("z", None, []))
        print 'raised event in x3'
    
    def _x_receiving_receiving_0_exec(self, parameters):
        print 'received event...'
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/x"].getEffectiveTargetStates()
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

class Controller(ThreadsControllerBase):
    def __init__(self, keep_running = None, behind_schedule_callback = None):
        if keep_running == None: keep_running = True
        if behind_schedule_callback == None: behind_schedule_callback = None
        ThreadsControllerBase.__init__(self, ObjectManager(self), keep_running, behind_schedule_callback)
        self.object_manager.createInstance("A", [])