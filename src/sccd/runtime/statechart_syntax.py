from dataclasses import dataclass, field
from typing import *
from sccd.runtime.event_queue import Timestamp
from sccd.compiler.utils import FormattedWriter

@dataclass
class Action:
    pass

class State:
    def __init__(self, short_name):
        # 'id' attribute of the state in XML. possibly not unique within the statechart
        self.short_name = short_name
        # "full name", unique within the statechart
        self.name = ""
        
        self.parent = None
        self.children = []
        self.default_state = None
        self.transitions = []
        self.enter: List[Action] = []
        self.exit: List[Action] = []
        self.history = [] # list of history states that are children

        # optimization stuff
        self.state_id = -1
        self.ancestors = []
        self.descendants = []
        self.descendant_bitmap = 0
        self.has_eventless_transitions = False

    def getEffectiveTargetStates(self, instance):
        targets = [self]
        if self.default_state:
            targets.extend(self.default_state.getEffectiveTargetStates(instance))
        return targets

    # Recursively assigns unique state_id to each state in the tree,
    # as well as some other optimization stuff
    # Should only be called once for the root of the state tree,
    # after the tree has been built.
    # Returns state_id + total number of states in tree
    def init_tree(self, state_id: int = 0, name_prefix: str = "", states = {}) -> int:
        self.state_id = state_id
        next_id = state_id + 1
        self.name = name_prefix + self.short_name if name_prefix == '/' else name_prefix + '/' + self.short_name
        states[self.name] = self
        for i, c in enumerate(self.children):
            if isinstance(c, HistoryState):
                self.history.append(c)
            c.parent = self
            c.ancestors.append(self)
            c.ancestors.extend(self.ancestors)
            next_id = c.init_tree(next_id, self.name, states)
        self.descendants.extend(self.children)
        for c in self.children:
            self.descendants.extend(c.descendants)
        for d in self.descendants:
            self.descendant_bitmap |= 2**d.state_id
        return next_id

    def print(self, w = FormattedWriter()):
        w.write(self.name)
        w.indent()
        for c in self.children:
            c.print(w)
        w.dedent()
            
    def addChild(self, child):
        self.children.append(child)
    
    def addTransition(self, transition):
        self.transitions.append(transition)
        
    def setEnter(self, enter: List[Action]):
        self.enter = enter
        
    def setExit(self, exit: List[Action]):
        self.exit = exit
                    
    def __repr__(self):
        return "State(%s)" % (self.state_id)
        
class HistoryState(State):
    def __init__(self, name):
        State.__init__(self, name)
        
class ShallowHistoryState(HistoryState):
    def __init__(self, name):
        HistoryState.__init__(self, name)
        
    def getEffectiveTargetStates(self, instance):
        if self.state_id in instance.history_values:
            targets = []
            for hv in instance.history_values[self.state_id]:
                targets.extend(hv.getEffectiveTargetStates(instance))
            return targets
        else:
            # TODO: is it correct that in this case, the parent itself is also entered?
            return self.parent.getEffectiveTargetStates(instance)
        
class DeepHistoryState(HistoryState):
    def __init__(self, name):
        HistoryState.__init__(self, name)
        
    def getEffectiveTargetStates(self, instance):
        if self.state_id in instance.history_values:
            return instance.history_values[self.state_id]
        else:
            # TODO: is it correct that in this case, the parent itself is also entered?
            return self.parent.getEffectiveTargetStates(instance)
        
class ParallelState(State):
    def __init__(self, name):
        State.__init__(self, name)
        
    def getEffectiveTargetStates(self, instance):
        targets = [self]
        for c in self.children:
            if not isinstance(c, HistoryState):
                targets.extend(c.getEffectiveTargetStates(instance))
        return targets

@dataclass
class Trigger:
    name: str
    port: str

class Transition:
    def __init__(self, source, targets: List[State]):
        self.guard = None
        self.actions: List[Action] = []
        self.trigger: Optional[Trigger] = None
        self.source = source
        self.targets = targets
        self.enabled_event = None # the event that enabled this transition
        self.optimize()
                    
    def setGuard(self, guard):
        self.guard = guard
        
    def setActions(self, actions):
        self.actions = actions
    
    def setTrigger(self, trigger):
        self.trigger = trigger
        if self.trigger is None:
            self.source.has_eventless_transitions = True
        
    def optimize(self):
        # the least-common ancestor can be computed statically
        if self.source in self.targets[0].ancestors:
            self.lca = self.source
        else:
            self.lca = self.source.parent
            target = self.targets[0]
            if self.source.parent != target.parent: # external
                for a in self.source.ancestors:
                    if a in target.ancestors:
                        self.lca = a
                        break
                    
    def __repr__(self):
        return "Transition(%s, %s)" % (self.source, self.targets[0])


@dataclass
class Expression:
    pass


@dataclass
class RaiseEvent(Action):
    name: str
    parameters: List[Expression]

    # just a simple string representation for rendering a transition label
    def render(self) -> str:
        return '^'+self.name

@dataclass
class RaiseInternalEvent(RaiseEvent):
    pass

@dataclass
class RaiseOutputEvent(RaiseEvent):
    outport: str
    time_offset: Timestamp

    def render(self) -> str:
        return '^'+self.outport + '.' + self.name
