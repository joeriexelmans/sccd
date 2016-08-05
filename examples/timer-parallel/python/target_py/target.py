"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Fri Aug 05 16:08:36 2016

Model author: Simon Van Mierlo
Model name:   Timer (Threaded Version)

"""

from sccd.runtime.statecharts_core import *
from sccd.runtime.accurate_time import time

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
    def print_simulated_time(self):
        print 'SIMTIME = %.2f' % get_simulated_time()
    
    
    # user defined method
    def print_wct_time(self):
        print 'ACTTIME = %.2f' % time()
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, self)
        
        # state /running
        self.states["/running"] = ParallelState(1, self)
        
        # state /running/print_simulated_time
        self.states["/running/print_simulated_time"] = State(2, self)
        
        # state /running/print_simulated_time/print_simulated_time
        self.states["/running/print_simulated_time/print_simulated_time"] = State(3, self)
        self.states["/running/print_simulated_time/print_simulated_time"].setEnter(self._running_print_simulated_time_print_simulated_time_enter)
        self.states["/running/print_simulated_time/print_simulated_time"].setExit(self._running_print_simulated_time_print_simulated_time_exit)
        
        # state /running/print_wct_time
        self.states["/running/print_wct_time"] = State(4, self)
        
        # state /running/print_wct_time/print_wct_time
        self.states["/running/print_wct_time/print_wct_time"] = State(5, self)
        self.states["/running/print_wct_time/print_wct_time"].setEnter(self._running_print_wct_time_print_wct_time_enter)
        self.states["/running/print_wct_time/print_wct_time"].setExit(self._running_print_wct_time_print_wct_time_exit)
        
        # state /interrupted
        self.states["/interrupted"] = State(6, self)
        
        # add children
        self.states[""].addChild(self.states["/running"])
        self.states[""].addChild(self.states["/interrupted"])
        self.states["/running"].addChild(self.states["/running/print_simulated_time"])
        self.states["/running"].addChild(self.states["/running/print_wct_time"])
        self.states["/running/print_simulated_time"].addChild(self.states["/running/print_simulated_time/print_simulated_time"])
        self.states["/running/print_wct_time"].addChild(self.states["/running/print_wct_time/print_wct_time"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/running"]
        self.states["/running/print_simulated_time"].default_state = self.states["/running/print_simulated_time/print_simulated_time"]
        self.states["/running/print_wct_time"].default_state = self.states["/running/print_wct_time/print_wct_time"]
        
        # transition /running/print_simulated_time/print_simulated_time
        _running_print_simulated_time_print_simulated_time_0 = Transition(self, self.states["/running/print_simulated_time/print_simulated_time"], [self.states["/running/print_simulated_time/print_simulated_time"]])
        _running_print_simulated_time_print_simulated_time_0.setAction(self._running_print_simulated_time_print_simulated_time_0_exec)
        _running_print_simulated_time_print_simulated_time_0.setTrigger(Event("_0after"))
        self.states["/running/print_simulated_time/print_simulated_time"].addTransition(_running_print_simulated_time_print_simulated_time_0)
        
        # transition /running/print_wct_time/print_wct_time
        _running_print_wct_time_print_wct_time_0 = Transition(self, self.states["/running/print_wct_time/print_wct_time"], [self.states["/running/print_wct_time/print_wct_time"]])
        _running_print_wct_time_print_wct_time_0.setAction(self._running_print_wct_time_print_wct_time_0_exec)
        _running_print_wct_time_print_wct_time_0.setTrigger(Event("_1after"))
        self.states["/running/print_wct_time/print_wct_time"].addTransition(_running_print_wct_time_print_wct_time_0)
        
        # transition /interrupted
        _interrupted_0 = Transition(self, self.states["/interrupted"], [self.states["/interrupted"]])
        _interrupted_0.setAction(self._interrupted_0_exec)
        _interrupted_0.setTrigger(Event("interrupt", "input"))
        self.states["/interrupted"].addTransition(_interrupted_0)
        _interrupted_1 = Transition(self, self.states["/interrupted"], [self.states["/running"]])
        _interrupted_1.setAction(self._interrupted_1_exec)
        _interrupted_1.setTrigger(Event("continue", "input"))
        self.states["/interrupted"].addTransition(_interrupted_1)
        
        # transition /running
        _running_0 = Transition(self, self.states["/running"], [self.states["/interrupted"]])
        _running_0.setAction(self._running_0_exec)
        _running_0.setTrigger(Event("interrupt", "input"))
        self.states["/running"].addTransition(_running_0)
        
        # transition /running/print_simulated_time
        _running_print_simulated_time_0 = Transition(self, self.states["/running/print_simulated_time"], [self.states["/running/print_simulated_time"]])
        _running_print_simulated_time_0.setAction(self._running_print_simulated_time_0_exec)
        _running_print_simulated_time_0.setTrigger(Event("interrupt", "input"))
        self.states["/running/print_simulated_time"].addTransition(_running_print_simulated_time_0)
    
    def _running_print_simulated_time_print_simulated_time_enter(self):
        self.addTimer(0, 0.05)
    
    def _running_print_simulated_time_print_simulated_time_exit(self):
        self.removeTimer(0)
    
    def _running_print_wct_time_print_wct_time_enter(self):
        self.addTimer(1, 0.05)
    
    def _running_print_wct_time_print_wct_time_exit(self):
        self.removeTimer(1)
    
    def _running_0_exec(self, parameters):
        self.print_simulated_time()
        self.print_wct_time()
    
    def _running_print_simulated_time_0_exec(self, parameters):
        print 'going nowhere'
    
    def _running_print_simulated_time_print_simulated_time_0_exec(self, parameters):
        self.print_simulated_time()
    
    def _running_print_wct_time_print_wct_time_0_exec(self, parameters):
        self.print_wct_time()
    
    def _interrupted_0_exec(self, parameters):
        self.print_simulated_time()
        self.print_wct_time()
    
    def _interrupted_1_exec(self, parameters):
        self.print_simulated_time()
        self.print_wct_time()
    
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
        else:
            raise Exception("Cannot instantiate class " + class_name)
        return instance

class Controller(ThreadsControllerBase):
    def __init__(self, keep_running = None):
        if keep_running == None: keep_running = True
        ThreadsControllerBase.__init__(self, ObjectManager(self), keep_running)
        self.addInputPort("input")
        self.object_manager.createInstance("MainApp", [])