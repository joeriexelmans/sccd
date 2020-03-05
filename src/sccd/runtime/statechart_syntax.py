class State:
    def __init__(self, name, obj):
        self.name = name
        self.obj = obj
        
        self.parent = None
        self.children = []
        self.default_state = None
        self.transitions = []
        self.enter = None
        self.exit = None
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
    def init_tree(self, root_state_id: int = 0) -> int:
        self.state_id = root_state_id
        next_id = root_state_id + 1
        for i, c in enumerate(self.children):
            if isinstance(c, HistoryState):
                self.history.append(c)
            c.parent = self
            c.ancestors.append(self)
            c.ancestors.extend(self.ancestors)
            next_id += c.init_tree(next_id)
        self.descendants.extend(self.children)
        for c in self.children:
            self.descendants.extend(c.descendants)
        for d in self.descendants:
            self.descendant_bitmap |= 2**d.state_id
        return 1 + len(self.descendants)
            
    def addChild(self, child):
        self.children.append(child)
    
    def addTransition(self, transition):
        self.transitions.append(transition)
        
    def setEnter(self, enter):
        self.enter = enter
        
    def setExit(self, exit):
        self.exit = exit
                    
    def __repr__(self):
        return "State(%s)" % (self.state_id)
        
class HistoryState(State):
    def __init__(self, name, obj):
        State.__init__(self, name, obj)
        
class ShallowHistoryState(HistoryState):
    def __init__(self, name, obj):
        HistoryState.__init__(self, name, obj)
        
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
    def __init__(self, name, obj):
        HistoryState.__init__(self, name, obj)
        
    def getEffectiveTargetStates(self, instance):
        if self.state_id in instance.history_values:
            return instance.history_values[self.state_id]
        else:
            # TODO: is it correct that in this case, the parent itself is also entered?
            return self.parent.getEffectiveTargetStates(instance)
        
class ParallelState(State):
    def __init__(self, name, obj):
        State.__init__(self, name, obj)
        
    def getEffectiveTargetStates(self, instance):
        targets = [self]
        for c in self.children:
            if not isinstance(c, HistoryState):
                targets.extend(c.getEffectiveTargetStates(instance))
        return targets

class Transition:
    def __init__(self, source, targets):
        self.guard = None
        self.action = None
        self.trigger = None
        self.source = source
        self.targets = targets
        self.enabled_event = None # the event that enabled this transition
        self.optimize()
                    
    def setGuard(self, guard):
        self.guard = guard
        
    def setAction(self, action):
        self.action = action
    
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
