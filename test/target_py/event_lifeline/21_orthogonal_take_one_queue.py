"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Tue Aug 09 09:35:56 2016

Model author: Herr Joeri Exelmans
Model name:   orthogonal_take_one_queue
Model description:
Internal event lifeline - Queue-semantics: Internal events are treated just like external events: They are added to the object's event queue and will be sensed in another big step. This way, a raised internal event will always be sensed at some point later in time, but it is possible that other (external) events in the object's event queue are treated first.
"""

from sccd.runtime.statecharts_core import *

# package "orthogonal_take_one_queue"

class c(RuntimeClassBase):
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
        c.user_defined_constructor(self)
    
    def user_defined_constructor(self):
        pass
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, self)
        
        # state /p
        self.states["/p"] = ParallelState(1, self)
        
        # state /p/o0
        self.states["/p/o0"] = State(2, self)
        
        # state /p/o0/sa
        self.states["/p/o0/sa"] = State(3, self)
        self.states["/p/o0/sa"].setEnter(self._p_o0_sa_enter)
        
        # state /p/o0/sb
        self.states["/p/o0/sb"] = State(4, self)
        self.states["/p/o0/sb"].setEnter(self._p_o0_sb_enter)
        
        # state /p/o1
        self.states["/p/o1"] = State(5, self)
        
        # state /p/o1/sc
        self.states["/p/o1/sc"] = State(6, self)
        self.states["/p/o1/sc"].setEnter(self._p_o1_sc_enter)
        
        # state /p/o1/sd
        self.states["/p/o1/sd"] = State(7, self)
        self.states["/p/o1/sd"].setEnter(self._p_o1_sd_enter)
        
        # state /p/o1/se
        self.states["/p/o1/se"] = State(8, self)
        self.states["/p/o1/se"].setEnter(self._p_o1_se_enter)
        
        # add children
        self.states[""].addChild(self.states["/p"])
        self.states["/p"].addChild(self.states["/p/o0"])
        self.states["/p"].addChild(self.states["/p/o1"])
        self.states["/p/o0"].addChild(self.states["/p/o0/sa"])
        self.states["/p/o0"].addChild(self.states["/p/o0/sb"])
        self.states["/p/o1"].addChild(self.states["/p/o1/sc"])
        self.states["/p/o1"].addChild(self.states["/p/o1/sd"])
        self.states["/p/o1"].addChild(self.states["/p/o1/se"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/p"]
        self.states["/p/o0"].default_state = self.states["/p/o0/sa"]
        self.states["/p/o1"].default_state = self.states["/p/o1/sc"]
        
        # transition /p/o0/sa
        _p_o0_sa_0 = Transition(self, self.states["/p/o0/sa"], [self.states["/p/o0/sb"]])
        _p_o0_sa_0.setAction(self._p_o0_sa_0_exec)
        _p_o0_sa_0.setTrigger(Event("f", None))
        self.states["/p/o0/sa"].addTransition(_p_o0_sa_0)
        
        # transition /p/o0/sb
        _p_o0_sb_0 = Transition(self, self.states["/p/o0/sb"], [self.states["/p/o0/sa"]])
        _p_o0_sb_0.setTrigger(None)
        self.states["/p/o0/sb"].addTransition(_p_o0_sb_0)
        
        # transition /p/o1/sc
        _p_o1_sc_0 = Transition(self, self.states["/p/o1/sc"], [self.states["/p/o1/sd"]])
        _p_o1_sc_0.setAction(self._p_o1_sc_0_exec)
        _p_o1_sc_0.setTrigger(Event("e", "in"))
        self.states["/p/o1/sc"].addTransition(_p_o1_sc_0)
        
        # transition /p/o1/sd
        _p_o1_sd_0 = Transition(self, self.states["/p/o1/sd"], [self.states["/p/o1/se"]])
        _p_o1_sd_0.setTrigger(Event("g", None))
        self.states["/p/o1/sd"].addTransition(_p_o1_sd_0)
    
    def _p_o0_sa_enter(self):
        self.big_step.outputEvent(Event("entered_sa", "out", []))
    
    def _p_o0_sb_enter(self):
        self.big_step.outputEvent(Event("entered_sb", "out", []))
    
    def _p_o1_sc_enter(self):
        self.big_step.outputEvent(Event("entered_sc", "out", []))
    
    def _p_o1_sd_enter(self):
        self.big_step.outputEvent(Event("entered_sd", "out", []))
    
    def _p_o1_se_enter(self):
        self.big_step.outputEvent(Event("entered_se", "out", []))
    
    def _p_o0_sa_0_exec(self, parameters):
        self.raiseInternalEvent(Event("g", None, []))
    
    def _p_o1_sc_0_exec(self, parameters):
        self.raiseInternalEvent(Event("f", None, []))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/p"].getEffectiveTargetStates()
        RuntimeClassBase.initializeStatechart(self)

class ObjectManager(ObjectManagerBase):
    def __init__(self, controller):
        ObjectManagerBase.__init__(self, controller)
    
    def instantiate(self, class_name, construct_params):
        if class_name == "c":
            instance = c(self.controller)
            instance.associations = {}
        else:
            raise Exception("Cannot instantiate class " + class_name)
        return instance

class Controller(ThreadsControllerBase):
    def __init__(self, keep_running = None, behind_schedule_callback = None):
        if keep_running == None: keep_running = True
        if behind_schedule_callback == None: behind_schedule_callback = None
        ThreadsControllerBase.__init__(self, ObjectManager(self), keep_running, behind_schedule_callback)
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
    expected_events = [[Event("entered_sa", "out", []), Event("entered_sc", "out", [])], [Event("entered_sd", "out", [])], [Event("entered_sb", "out", [])], [Event("entered_sa", "out", []), Event("entered_se", "out", [])]]