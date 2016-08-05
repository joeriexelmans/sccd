"""
Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)

Date:   Fri Aug 05 16:13:35 2016

Model author: Herr Joeri Exelmans
Model name:   source_parent_history

"""

from sccd.runtime.statecharts_core import *

# package "source_parent_history"

class c(RuntimeClassBase):
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
        c.user_defined_constructor(self)
    
    def user_defined_constructor(self):
        pass
    
    def user_defined_destructor(self):
        pass
    
    
    # builds Statechart structure
    def build_statechart_structure(self):
        
        # state <root>
        self.states[""] = State(0, self)
        
        # state /main
        self.states["/main"] = State(1, self)
        
        # state /main/history
        self.states["/main/history"] = ShallowHistoryState(2, self)
        
        # state /main/A
        self.states["/main/A"] = State(3, self)
        
        # state /main/B
        self.states["/main/B"] = State(4, self)
        
        # add children
        self.states[""].addChild(self.states["/main"])
        self.states["/main"].addChild(self.states["/main/history"])
        self.states["/main"].addChild(self.states["/main/A"])
        self.states["/main"].addChild(self.states["/main/B"])
        self.states[""].fixTree()
        self.states[""].default_state = self.states["/main"]
        self.states["/main"].default_state = self.states["/main/A"]
        
        # transition /main/A
        _main_A_0 = Transition(self, self.states["/main/A"], [self.states["/main/B"]])
        _main_A_0.setAction(self._main_A_0_exec)
        _main_A_0.setTrigger(Event("e", "in"))
        self.states["/main/A"].addTransition(_main_A_0)
        
        # transition /main
        _main_0 = Transition(self, self.states["/main"], [self.states["/main/history"]])
        _main_0.setAction(self._main_0_exec)
        _main_0.setTrigger(Event("e", "in"))
        self.states["/main"].addTransition(_main_0)
    
    def _main_0_exec(self, parameters):
        self.big_step.outputEvent(Event("to_history", "out", []))
    
    def _main_A_0_exec(self, parameters):
        self.big_step.outputEvent(Event("to_B", "out", []))
    
    def initializeStatechart(self):
        # enter default state
        states = self.states["/main"].getEffectiveTargetStates()
        self.updateConfiguration(states)
        for state in states:
            if state.enter:
                state.enter()

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
    def __init__(self, keep_running = None):
        if keep_running == None: keep_running = True
        ThreadsControllerBase.__init__(self, ObjectManager(self), keep_running)
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
    expected_events = [[Event("to_history", "out", [])]]