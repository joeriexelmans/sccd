"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Wed Aug 03 16:10:23 2016

Model author: Glenn De Jonghe
Model name:   TestHistoryDeep
Model description:
Testing history deep.
"""

from python_runtime.statecharts_core import *

# package "TestHistoryDeep"

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
        
        # state /parallel
        self.states["/parallel"] = ParallelState(1, self)
        
        # state /parallel/orthogonal
        self.states["/parallel/orthogonal"] = State(2, self)
        
        # state /parallel/orthogonal/wrapper
        self.states["/parallel/orthogonal/wrapper"] = State(3, self)
        
        # state /parallel/orthogonal/wrapper/state_1
        self.states["/parallel/orthogonal/wrapper/state_1"] = State(4, self)
        
        # state /parallel/orthogonal/wrapper/state_1/inner_1
        self.states["/parallel/orthogonal/wrapper/state_1/inner_1"] = State(5, self)
        
        # state /parallel/orthogonal/wrapper/state_1/inner_2
        self.states["/parallel/orthogonal/wrapper/state_1/inner_2"] = State(6, self)
        
        # state /parallel/orthogonal/wrapper/state_2
        self.states["/parallel/orthogonal/wrapper/state_2"] = State(7, self)
        
        # state /parallel/orthogonal/wrapper/state_2/inner_3
        self.states["/parallel/orthogonal/wrapper/state_2/inner_3"] = State(8, self)
        
        # state /parallel/orthogonal/wrapper/state_2/inner_4
        self.states["/parallel/orthogonal/wrapper/state_2/inner_4"] = State(9, self)
        
        # state /parallel/orthogonal/wrapper/history
        self.states["/parallel/orthogonal/wrapper/history"] = DeepHistoryState(10, self)
        
        # state /parallel/orthogonal/outer
        self.states["/parallel/orthogonal/outer"] = State(11, self)
        
        # state /parallel/orthogonal_tester
        self.states["/parallel/orthogonal_tester"] = State(12, self)
        
        # state /parallel/orthogonal_tester/start
        self.states["/parallel/orthogonal_tester/start"] = State(13, self)
        
        # state /parallel/orthogonal_tester/step1
        self.states["/parallel/orthogonal_tester/step1"] = State(14, self)
        
        # state /parallel/orthogonal_tester/step2
        self.states["/parallel/orthogonal_tester/step2"] = State(15, self)
        
        # state /parallel/orthogonal_tester/step3
        self.states["/parallel/orthogonal_tester/step3"] = State(16, self)
        
        # state /parallel/orthogonal_tester/end
        self.states["/parallel/orthogonal_tester/end"] = State(17, self)
        
        # add children
        self.states[""].addChild(self.states["/parallel"])
        self.states["/parallel"].addChild(self.states["/parallel/orthogonal"])
        self.states["/parallel"].addChild(self.states["/parallel/orthogonal_tester"])
        self.states["/parallel/orthogonal"].addChild(self.states["/parallel/orthogonal/wrapper"])
        self.states["/parallel/orthogonal"].addChild(self.states["/parallel/orthogonal/outer"])
        self.states["/parallel/orthogonal/wrapper"].addChild(self.states["/parallel/orthogonal/wrapper/state_1"])
        self.states["/parallel/orthogonal/wrapper"].addChild(self.states["/parallel/orthogonal/wrapper/state_2"])
        self.states["/parallel/orthogonal/wrapper"].addChild(self.states["/parallel/orthogonal/wrapper/history"])
        self.states["/parallel/orthogonal/wrapper/state_1"].addChild(self.states["/parallel/orthogonal/wrapper/state_1/inner_1"])
        self.states["/parallel/orthogonal/wrapper/state_1"].addChild(self.states["/parallel/orthogonal/wrapper/state_1/inner_2"])
        self.states["/parallel/orthogonal/wrapper/state_2"].addChild(self.states["/parallel/orthogonal/wrapper/state_2/inner_3"])
        self.states["/parallel/orthogonal/wrapper/state_2"].addChild(self.states["/parallel/orthogonal/wrapper/state_2/inner_4"])
        self.states["/parallel/orthogonal_tester"].addChild(self.states["/parallel/orthogonal_tester/start"])
        self.states["/parallel/orthogonal_tester"].addChild(self.states["/parallel/orthogonal_tester/step1"])
        self.states["/parallel/orthogonal_tester"].addChild(self.states["/parallel/orthogonal_tester/step2"])
        self.states["/parallel/orthogonal_tester"].addChild(self.states["/parallel/orthogonal_tester/step3"])
        self.states["/parallel/orthogonal_tester"].addChild(self.states["/parallel/orthogonal_tester/end"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/parallel"]
        self.states["/parallel/orthogonal"].default_state = self.states["/parallel/orthogonal/wrapper"]
        self.states["/parallel/orthogonal/wrapper"].default_state = self.states["/parallel/orthogonal/wrapper/state_1"]
        self.states["/parallel/orthogonal/wrapper/state_1"].default_state = self.states["/parallel/orthogonal/wrapper/state_1/inner_1"]
        self.states["/parallel/orthogonal/wrapper/state_2"].default_state = self.states["/parallel/orthogonal/wrapper/state_2/inner_3"]
        self.states["/parallel/orthogonal_tester"].default_state = self.states["/parallel/orthogonal_tester/start"]
        
        # transition /parallel/orthogonal/wrapper/state_2/inner_3
        _parallel_orthogonal_wrapper_state_2_inner_3_0 = Transition(self, self.states["/parallel/orthogonal/wrapper/state_2/inner_3"], [self.states["/parallel/orthogonal/wrapper/state_2/inner_4"]])
        _parallel_orthogonal_wrapper_state_2_inner_3_0.trigger = Event("to_inner_4", None)
        self.states["/parallel/orthogonal/wrapper/state_2/inner_3"].addTransition(_parallel_orthogonal_wrapper_state_2_inner_3_0)
        
        # transition /parallel/orthogonal/outer
        _parallel_orthogonal_outer_0 = Transition(self, self.states["/parallel/orthogonal/outer"], [self.states["/parallel/orthogonal/wrapper/history"]])
        _parallel_orthogonal_outer_0.trigger = Event("to_history", None)
        self.states["/parallel/orthogonal/outer"].addTransition(_parallel_orthogonal_outer_0)
        
        # transition /parallel/orthogonal_tester/start
        _parallel_orthogonal_tester_start_0 = Transition(self, self.states["/parallel/orthogonal_tester/start"], [self.states["/parallel/orthogonal_tester/step1"]])
        _parallel_orthogonal_tester_start_0.setAction(self._parallel_orthogonal_tester_start_0_exec)
        self.states["/parallel/orthogonal_tester/start"].addTransition(_parallel_orthogonal_tester_start_0)
        
        # transition /parallel/orthogonal_tester/step1
        _parallel_orthogonal_tester_step1_0 = Transition(self, self.states["/parallel/orthogonal_tester/step1"], [self.states["/parallel/orthogonal_tester/step2"]])
        _parallel_orthogonal_tester_step1_0.setAction(self._parallel_orthogonal_tester_step1_0_exec)
        _parallel_orthogonal_tester_step1_0.setGuard(self._parallel_orthogonal_tester_step1_0_guard)
        self.states["/parallel/orthogonal_tester/step1"].addTransition(_parallel_orthogonal_tester_step1_0)
        
        # transition /parallel/orthogonal_tester/step2
        _parallel_orthogonal_tester_step2_0 = Transition(self, self.states["/parallel/orthogonal_tester/step2"], [self.states["/parallel/orthogonal_tester/step3"]])
        _parallel_orthogonal_tester_step2_0.setAction(self._parallel_orthogonal_tester_step2_0_exec)
        _parallel_orthogonal_tester_step2_0.setGuard(self._parallel_orthogonal_tester_step2_0_guard)
        self.states["/parallel/orthogonal_tester/step2"].addTransition(_parallel_orthogonal_tester_step2_0)
        
        # transition /parallel/orthogonal_tester/step3
        _parallel_orthogonal_tester_step3_0 = Transition(self, self.states["/parallel/orthogonal_tester/step3"], [self.states["/parallel/orthogonal_tester/end"]])
        _parallel_orthogonal_tester_step3_0.setAction(self._parallel_orthogonal_tester_step3_0_exec)
        _parallel_orthogonal_tester_step3_0.setGuard(self._parallel_orthogonal_tester_step3_0_guard)
        self.states["/parallel/orthogonal_tester/step3"].addTransition(_parallel_orthogonal_tester_step3_0)
        
        # transition /parallel/orthogonal/wrapper
        _parallel_orthogonal_wrapper_0 = Transition(self, self.states["/parallel/orthogonal/wrapper"], [self.states["/parallel/orthogonal/outer"]])
        _parallel_orthogonal_wrapper_0.trigger = Event("to_outer", None)
        self.states["/parallel/orthogonal/wrapper"].addTransition(_parallel_orthogonal_wrapper_0)
        
        # transition /parallel/orthogonal/wrapper/state_1
        _parallel_orthogonal_wrapper_state_1_0 = Transition(self, self.states["/parallel/orthogonal/wrapper/state_1"], [self.states["/parallel/orthogonal/wrapper/state_2"]])
        _parallel_orthogonal_wrapper_state_1_0.trigger = Event("to_state_2", None)
        self.states["/parallel/orthogonal/wrapper/state_1"].addTransition(_parallel_orthogonal_wrapper_state_1_0)
    
    def _parallel_orthogonal_tester_start_0_exec(self, parameters):
        self.raiseInternalEvent(Event("to_state_2", None, []))
        self.raiseInternalEvent(Event("to_inner_4", None, []))
    
    def _parallel_orthogonal_tester_step1_0_exec(self, parameters):
        self.big_step.outputEvent(Event("check1", "test_output", []))
        self.raiseInternalEvent(Event("to_outer", None, []))
    
    def _parallel_orthogonal_tester_step1_0_guard(self, parameters):
        return self.inState(["/parallel/orthogonal/wrapper/state_2/inner_4"])
    
    def _parallel_orthogonal_tester_step2_0_exec(self, parameters):
        self.big_step.outputEvent(Event("check2", "test_output", []))
        self.raiseInternalEvent(Event("to_history", None, []))
    
    def _parallel_orthogonal_tester_step2_0_guard(self, parameters):
        return self.inState(["/parallel/orthogonal/outer"])
    
    def _parallel_orthogonal_tester_step3_0_exec(self, parameters):
        self.big_step.outputEvent(Event("check3", "test_output", []))
    
    def _parallel_orthogonal_tester_step3_0_guard(self, parameters):
        return self.inState(["/parallel/orthogonal/wrapper/state_2/inner_4"])
    
    def initializeStatechart(self):
        # enter default state
        states = self.states["/parallel"].getEffectiveTargetStates()
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
        return instance

class Controller(ThreadsControllerBase):
    def __init__(self, keep_running = None):
        if keep_running == None: keep_running = True
        ThreadsControllerBase.__init__(self, ObjectManager(self), keep_running)
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
    expected_events = [[Event("check1", "test_output", [])], [Event("check2", "test_output", [])], [Event("check3", "test_output", [])]]