import termcolor
from typing import *
from sccd.syntax.action import *
from sccd.util.bitmap import *

@dataclass
class State:
    short_name: str # value of 'id' attribute in XML
    parent: Optional['State'] # only None if root state

    children: List['State'] = field(default_factory=list)
    default_state = None

    transitions: List['Transition'] = field(default_factory=list)

    enter: List[Action] = field(default_factory=list)
    exit: List[Action] = field(default_factory=list)

    gen: Optional['StateGenerated'] = None

    def __post_init__(self):
        if self.parent is not None:
            self.parent.children.append(self)

    def getEffectiveTargetStates(self, instance):
        targets = [self]
        if self.default_state:
            targets.extend(self.default_state.getEffectiveTargetStates(instance))
        return targets

    # # Recursively assigns unique state_id to each state in the tree,
    # # as well as some other optimization stuff
    # # Should only be called once for the root of the state tree,
    # # after the tree has been built.
    # # Returns state_id + total number of states in tree
    # def init_tree(self, state_id: int = 0, name_prefix: str = "", states = {}, state_list = [], transition_list = []) -> int:
    #     self.state_id = state_id
    #     next_id = state_id + 1
    #     self.name = name_prefix + self.short_name if name_prefix == '/' else name_prefix + '/' + self.short_name
    #     states[self.name] = self
    #     state_list.append(self)
    #     for t in self.transitions:
    #         transition_list.append(t)
    #     for i, c in enumerate(self.children):
    #         if isinstance(c, HistoryState):
    #             self.history.append(c)
    #         c.parent = self
    #         c.ancestors.append(self)
    #         c.ancestors.extend(self.ancestors)
    #         next_id = c.init_tree(next_id, self.name, states, state_list, transition_list)
    #     self.descendants.extend(self.children)
    #     for c in self.children:
    #         self.descendants.extend(c.descendants)
    #     for d in self.descendants:
    #         self.descendant_bitmap |= bit(d.state_id)
    #     return next_id

    # def print(self, w = FormattedWriter()):
    #     w.write(self.name)
    #     w.indent()
    #     for c in self.children:
    #         c.print(w)
    #     w.dedent()
                    
    def __repr__(self):
        return "State(\"%s\")" % (self.gen.full_name)

# Generated fields (for optimization) of a state
@dataclass
class StateGenerated:
    state_id: int
    full_name: str
    ancestors: List[State] = field(default_factory=list) # order: close to far away, i.e. first element is parent
    descendants: List[State] = field(default_factory=list)  # order: breadth-first
    descendant_bitmap: Bitmap = Bitmap()
    history: List[State] = field(default_factory=list) # subset of children
    has_eventless_transitions: bool = False
    after_triggers: List['AfterTrigger'] = field(default_factory=list)


class HistoryState(State):
    pass
    # def __init__(self, name):
        # State.__init__(self, name)
        
class ShallowHistoryState(HistoryState):
    # def __init__(self, name):
        # HistoryState.__init__(self, name)
        
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
    # def __init__(self, name):
        # HistoryState.__init__(self, name)
        
    def getEffectiveTargetStates(self, instance):
        if self.state_id in instance.history_values:
            return instance.history_values[self.state_id]
        else:
            # TODO: is it correct that in this case, the parent itself is also entered?
            return self.parent.getEffectiveTargetStates(instance)
        
class ParallelState(State):
    # def __init__(self, name):
        # State.__init__(self, name)
        
    def getEffectiveTargetStates(self, instance):
        targets = [self]
        for c in self.children:
            if not isinstance(c, HistoryState):
                targets.extend(c.getEffectiveTargetStates(instance))
        return targets

@dataclass
class Trigger:
    id: int # event ID
    name: str # event name
    port: str

    def render(self) -> str:
        if self.port:
            return self.port+'.'+self.name
        else:
            return self.name

class AfterTrigger(Trigger):
    # id: unique within the statechart
    def __init__(self, id: int, name: str, delay: Expression):
        super().__init__(id=id, name=name, port="")
        self.delay = delay

        # Stateful variable, incremented each time a new future 'after' event is scheduled.
        # This is to distinguish multiple scheduled future events for the same after-transition.
        # Only one scheduled event should be responded to, i.e. the latest one.
        self.expected_id = -1

    def nextTimerId(self) -> int:
        self.expected_id += 1
        return self.expected_id

    def render(self) -> str:
        return "after("+self.delay.render()+")"


@dataclass
class Transition:
    source: State
    targets: List[State]

    guard: Optional[Expression] = None
    actions: List[Action] = field(default_factory=list)
    trigger: Optional[Trigger] = None

    gen: Optional['TransitionGenerated'] = None        
                    
    def __repr__(self):
        return termcolor.colored("%s 🡪 %s" % (self.source.gen.full_name, self.targets[0].gen.full_name), 'green')

# Generated fields (for optimization) of a transition
@dataclass
class TransitionGenerated:
    lca: State
    arena_bitmap: Bitmap

# @dataclass
class StateTree:

    # root: The root state of a state,transition tree structure with with all fields filled in,
    #       except the 'gen' fields. This function will fill in the 'gen' fields.
    def __init__(self, root: State):
        self.state_dict = {} # mapping from 'full name' to State
        self.state_list = [] # depth-first list of states
        self.transition_list = [] # all transitions in the tree, sorted by source state, depth-first

        next_id = 0

        def init_tree(state: State, parent_full_name: str, ancestors: List[State]):
            nonlocal next_id

            if state is root:
                full_name = '/'
            elif state.parent is root:
                full_name = '/' + state.short_name
            else:
                full_name = parent_full_name + '/' + state.short_name

            # full_name = parent_full_name + '/' + state.short_name

            state.gen = gen = StateGenerated(
                state_id=next_id,
                full_name=full_name,
                ancestors=ancestors)

            next_id += 1

            self.state_dict[gen.full_name] = state
            self.state_list.append(state)

            for t in state.transitions:
                self.transition_list.append(t)
                if t.trigger is None:
                    gen.has_eventless_transitions = True
                elif isinstance(t.trigger, AfterTrigger):
                    gen.after_triggers.append(t.trigger)

            for c in state.children:
                init_tree(c, gen.full_name, [state] + gen.ancestors)
                if isinstance(c, HistoryState):
                    gen.history.append(c)

            gen.descendants.extend(state.children)
            for c in state.children:
                gen.descendants.extend(c.gen.descendants)

            for d in gen.descendants:
                gen.descendant_bitmap |= bit(d.gen.state_id)

        init_tree(root, "", [])
        self.root = root


        def init_transition(t: Transition):
            # the least-common ancestor can be computed statically
            if t.source in t.targets[0].gen.ancestors:
                lca = t.source
            else:
                lca = t.source.parent
                target = t.targets[0]
                if t.source.parent != target.parent: # external
                    for a in t.source.gen.ancestors:
                        if a in target.gen.ancestors:
                            lca = a
                            break
            t.gen = TransitionGenerated(
                lca=lca,
                arena_bitmap=lca.gen.descendant_bitmap.set(lca.gen.state_id))

        for t in self.transition_list:
            init_transition(t)
