"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Tue Aug 02 14:25:10 2016

Model author: Simon Van Mierlo
Model name:   Timer (Threaded Version)

"""

from python_runtime.statecharts_core import *
from python_runtime.libs.ui import ui
from python_runtime.accurate_time import time

# package "Timer (Threaded Version)"

class MainApp(RuntimeClassBase):
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
        MainApp.user_defined_constructor(self)
    
    def user_defined_constructor(self):
        pass
    
    def user_defined_destructor(self):
        pass
    
    
    # user defined method
    def update_timers(self):
        print 'SIMTIME = %.2f' % get_simulated_time()
        print 'ACTTIME = %.2f' % time()
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state /running
        self.states["/running"] = State(0, self)
        self.states["/running"].setEnter(self._running_enter)
        self.states["/running"].setExit(self._running_exit)
        
        # state /interrupted
        self.states["/interrupted"] = State(1, self)
        
        # state <root>
        self.states[""] = State(2, self)
        
        # add children
        self.states[""].addChild(self.states["/running"])
        self.states[""].addChild(self.states["/interrupted"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/running"]
        
        # transition /running
        _running_0 = Transition(self, self.states["/running"], self.states["/running"])
        _running_0.setAction(self._running_0_exec)
        _running_0.trigger = Event("_0after")
        self.states["/running"].addTransition(_running_0)
        _running_1 = Transition(self, self.states["/running"], self.states["/interrupted"])
        _running_1.setAction(self._running_1_exec)
        _running_1.trigger = Event("interrupt", "input")
        self.states["/running"].addTransition(_running_1)
        
        # transition /interrupted
        _interrupted_0 = Transition(self, self.states["/interrupted"], self.states["/interrupted"])
        _interrupted_0.setAction(self._interrupted_0_exec)
        _interrupted_0.trigger = Event("interrupt", "input")
        self.states["/interrupted"].addTransition(_interrupted_0)
        _interrupted_1 = Transition(self, self.states["/interrupted"], self.states["/running"])
        _interrupted_1.setAction(self._interrupted_1_exec)
        _interrupted_1.trigger = Event("continue", "input")
        self.states["/interrupted"].addTransition(_interrupted_1)
    
    def _running_enter(self):
        self.addTimer(0, 0.05)
    
    def _running_exit(self):
        self.removeTimer(0)
    
    def _running_0_exec(self, parameters):
        self.update_timers()
    
    def _running_1_exec(self, parameters):
        self.update_timers()
    
    def _interrupted_0_exec(self, parameters):
        self.update_timers()
    
    def _interrupted_1_exec(self, parameters):
        self.update_timers()
    
    def initializeStatechart(self):
        # enter default state
        states = self.states["/running"].getEffectiveTargetStates()
        self.updateConfiguration(states)
        for state in states:
            if state.enter:
                state.enter()

class ObjectManager(ObjectManagerBase):
    def __init__(self, controller):
        ObjectManagerBase.__init__(self, controller)
    
    def instantiate(self, class_name, construct_params):
        if class_name == "MainApp":
            instance = MainApp(self.controller)
            instance.associations = {}
        return instance

class Controller(ThreadsControllerBase):
    def __init__(self, keep_running = None):
        if keep_running == None: keep_running = True
        ThreadsControllerBase.__init__(self, ObjectManager(self), keep_running)
        self.addInputPort("input")
        self.object_manager.createInstance("MainApp", [])