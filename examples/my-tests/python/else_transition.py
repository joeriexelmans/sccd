"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Wed May 30 12:03:02 2018

Model name:   else_transition_test

"""

from sccd.runtime.statecharts_core import *

# package "else_transition_test"

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
        self.x = 3
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, "", self)
        
        # state /main
        self.states["/main"] = ParallelState(1, "/main", self)
        
        # state /main/one
        self.states["/main/one"] = State(2, "/main/one", self)
        
        # state /main/one/A
        self.states["/main/one/A"] = State(3, "/main/one/A", self)
        
        # state /main/one/B
        self.states["/main/one/B"] = State(4, "/main/one/B", self)
        self.states["/main/one/B"].setEnter(self._main_one_B_enter)
        self.states["/main/one/B"].setExit(self._main_one_B_exit)
        
        # state /main/one/C
        self.states["/main/one/C"] = State(5, "/main/one/C", self)
        self.states["/main/one/C"].setEnter(self._main_one_C_enter)
        self.states["/main/one/C"].setExit(self._main_one_C_exit)
        
        # state /main/one/D
        self.states["/main/one/D"] = State(6, "/main/one/D", self)
        self.states["/main/one/D"].setEnter(self._main_one_D_enter)
        
        # state /main/two
        self.states["/main/two"] = State(7, "/main/two", self)
        
        # state /main/two/A
        self.states["/main/two/A"] = State(8, "/main/two/A", self)
        
        # state /main/two/B
        self.states["/main/two/B"] = State(9, "/main/two/B", self)
        
        # add children
        self.states[""].addChild(self.states["/main"])
        self.states["/main"].addChild(self.states["/main/one"])
        self.states["/main"].addChild(self.states["/main/two"])
        self.states["/main/one"].addChild(self.states["/main/one/A"])
        self.states["/main/one"].addChild(self.states["/main/one/B"])
        self.states["/main/one"].addChild(self.states["/main/one/C"])
        self.states["/main/one"].addChild(self.states["/main/one/D"])
        self.states["/main/two"].addChild(self.states["/main/two/A"])
        self.states["/main/two"].addChild(self.states["/main/two/B"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/main"]
        self.states["/main/one"].default_state = self.states["/main/one/A"]
        self.states["/main/two"].default_state = self.states["/main/two/A"]
        
        # transition /main/one/A
        _main_one_A_0 = Transition(self, self.states["/main/one/A"], [self.states["/main/one/B"]])
        _main_one_A_0.setTrigger(Event("a", None))
        _main_one_A_0.setGuard(self._main_one_A_0_guard)
        self.states["/main/one/A"].addTransition(_main_one_A_0)
        _main_one_A_1 = Transition(self, self.states["/main/one/A"], [self.states["/main/one/C"]])
        _main_one_A_1.setTrigger(Event("a", None))
        _main_one_A_1.setGuard(self._main_one_A_1_guard)
        self.states["/main/one/A"].addTransition(_main_one_A_1)
        _main_one_A_2 = Transition(self, self.states["/main/one/A"], [self.states["/main/one/D"]])
        _main_one_A_2.setTrigger(None)
        _main_one_A_2.setGuard(self._main_one_A_2_guard)
        self.states["/main/one/A"].addTransition(_main_one_A_2)
        
        # transition /main/one/B
        _main_one_B_0 = Transition(self, self.states["/main/one/B"], [self.states["/main/one/A"]])
        _main_one_B_0.setTrigger(Event("_0after"))
        self.states["/main/one/B"].addTransition(_main_one_B_0)
        
        # transition /main/one/C
        _main_one_C_0 = Transition(self, self.states["/main/one/C"], [self.states["/main/one/A"]])
        _main_one_C_0.setTrigger(Event("_1after"))
        self.states["/main/one/C"].addTransition(_main_one_C_0)
        
        # transition /main/two/A
        _main_two_A_0 = Transition(self, self.states["/main/two/A"], [self.states["/main/two/B"]])
        _main_two_A_0.setAction(self._main_two_A_0_exec)
        _main_two_A_0.setTrigger(None)
        self.states["/main/two/A"].addTransition(_main_two_A_0)
    
    def _main_one_B_enter(self):
        print "in B"
        self.addTimer(0, 0.05)
    
    def _main_one_B_exit(self):
        self.removeTimer(0)
    
    def _main_one_C_enter(self):
        print "in C"
        self.addTimer(1, 0.05)
    
    def _main_one_C_exit(self):
        self.removeTimer(1)
    
    def _main_one_D_enter(self):
        print "in D"
    
    def _main_one_A_0_guard(self, parameters):
        return self.x == 5
    
    def _main_one_A_1_guard(self, parameters):
        return "ELSE_GUARD"
    
    def _main_one_A_2_guard(self, parameters):
        return "ELSE_GUARD"
    
    def _main_two_A_0_exec(self, parameters):
        self.raiseInternalEvent(Event("a", None, []))
    
    def initializeStatechart(self):
        # enter default state
        self.default_targets = self.states["/main"].getEffectiveTargetStates()
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