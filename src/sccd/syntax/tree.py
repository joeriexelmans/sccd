import termcolor
from typing import *
from sccd.syntax.action import *
from sccd.util.bitmap import *


@dataclass
class State:
    short_name: str # value of 'id' attribute in XML
    parent: Optional['State'] # only None if root state

    stable: bool = False # whether this is a stable stabe. this field is ignored if maximality semantics is not set to SYNTACTIC

    children: List['State'] = field(default_factory=list)
    default_state = None # child state pointed to by 'initial' attribute

    transitions: List['Transition'] = field(default_factory=list)

    enter: List[Action] = field(default_factory=list)
    exit: List[Action] = field(default_factory=list)

    gen: Optional['StateOptimization'] = None

    def __post_init__(self):
        if self.parent is not None:
            self.parent.children.append(self)

    def getEffectiveTargetStates(self, instance):
        targets = [self]
        if self.default_state:
            targets.extend(self.default_state.getEffectiveTargetStates(instance))
        return targets
                    
    def __repr__(self):
        return "State(\"%s\")" % (self.gen.full_name)

# Generated fields (for optimization) of a state
@dataclass(frozen=True)
class StateOptimization:
    state_id: int
    state_id_bitmap: Bitmap
    full_name: str
    ancestors: List[State] # order: close to far away, i.e. first element is parent
    descendants: List[State]  # order: breadth-first
    descendant_bitmap: Bitmap
    history: List[State] # subset of children
    has_eventless_transitions: bool
    after_triggers: List['AfterTrigger']


class HistoryState(State):
    @abstractmethod
    def getEffectiveTargetStates(self, instance):
        pass
        
class ShallowHistoryState(HistoryState):
        
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
        
    def getEffectiveTargetStates(self, instance):
        if self.state_id in instance.history_values:
            return instance.history_values[self.state_id]
        else:
            # TODO: is it correct that in this case, the parent itself is also entered?
            return self.parent.getEffectiveTargetStates(instance)
        
class ParallelState(State):
        
    def getEffectiveTargetStates(self, instance):
        targets = [self]
        for c in self.children:
            if not isinstance(c, HistoryState):
                targets.extend(c.getEffectiveTargetStates(instance))
        return targets

@dataclass
class EventDecl:
    id: int
    name: str
    params_decl: List[ParamDecl]

    def render(self) -> str:
        if self.params_decl:
            return self.name + '(' + ', '.join(self.params_decl) + ')'
        else:
            return self.name

@dataclass
class Trigger:
    enabling: List[EventDecl]

    def __post_init__(self):
        self.enabling_bitmap = Bitmap.from_list(e.id for e in self.enabling)

    def check(self, events_bitmap: Bitmap) -> bool:
        return (self.enabling_bitmap & events_bitmap) == self.enabling_bitmap

    def render(self) -> str:
        return ' ∧ '.join(e.name for e in self.enabling)

@dataclass
class NegatedTrigger:
    enabling: List[EventDecl]
    disabling: List[EventDecl]

    def __post_init__(self):
        self.enabling_bitmap = Bitmap.from_list(e.id for e in self.enabling)
        self.disabling_bitmap = Bitmap.from_list(e.id for e in self.disabling)

    def check(self, events_bitmap: Bitmap) -> bool:
        return (self.enabling_bitmap & events_bitmap) == self.enabling_bitmap and not (self.disabling_bitmap & events_bitmap)

    def render(self) -> str:
        return ' ∧ '.join(e.name for e in self.enabling) + ' ∧ ' + ' ∧ '.join('¬'+e.name for e in self.disabling)

@dataclass
class EventTrigger:
    id: int # event ID
    name: str # event name
    port: str

    bitmap: Bitmap = None

    def __post_init__(self):
        self.bitmap = bit(self.id)

    def check(self, events_bitmap: Bitmap) -> bool:
        return (self.bitmap & events_bitmap) == self.bitmap

    def render(self) -> str:
        if self.port:
            return self.port+'.'+self.name
        else:
            return self.name

class NegatedEventTrigger(EventTrigger):
    pass

class AfterTrigger(EventTrigger):
    # id: unique within the statechart
    def __init__(self, id: int, name: str, after_id: int, delay: Expression):

        super().__init__(id=id, name=name, port="")
        self.after_id = after_id # unique ID for AfterTrigger
        self.delay = delay

    def render(self) -> str:
        return "after("+self.delay.render()+")"

@dataclass
class Transition:
    source: State
    targets: List[State]
    scope: Scope

    target_string: Optional[str] = None

    guard: Optional[Expression] = None
    actions: List[Action] = field(default_factory=list)
    trigger: Optional[EventTrigger] = None

    gen: Optional['TransitionOptimization'] = None        
                    
    def __repr__(self):
        return termcolor.colored("%s 🡪 %s" % (self.source.gen.full_name, self.targets[0].gen.full_name), 'green')

# Generated fields (for optimization) of a transition
@dataclass(frozen=True)
class TransitionOptimization:
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
        self.after_triggers = []
        self.stable_bitmap = Bitmap() # bitmap of state IDs of states that are stable. Only used for SYNTACTIC-maximality semantics.

        next_id = 0

        def init_state(state: State, parent_full_name: str, ancestors: List[State]):
            nonlocal next_id

            state_id = next_id
            next_id += 1

            if state is root:
                full_name = '/'
            elif state.parent is root:
                full_name = '/' + state.short_name
            else:
                full_name = parent_full_name + '/' + state.short_name

            self.state_dict[full_name] = state
            self.state_list.append(state)

            descendants = []
            history = []
            has_eventless_transitions = False
            after_triggers = []

            for t in state.transitions:
                self.transition_list.append(t)
                if t.trigger is None:
                    has_eventless_transitions = True
                elif isinstance(t.trigger, AfterTrigger):
                    after_triggers.append(t.trigger)
                    self.after_triggers.append(t.trigger)

            for c in state.children:
                init_state(c, full_name, [state] + ancestors)
                if isinstance(c, HistoryState):
                    history.append(c)

            descendants.extend(state.children)
            for c in state.children:
                descendants.extend(c.gen.descendants)

            state.gen = StateOptimization(
                state_id=state_id,
                state_id_bitmap=bit(state_id),
                full_name=full_name,
                ancestors=ancestors,
                descendants=descendants,
                descendant_bitmap=reduce(lambda x,y: x | bit(y.gen.state_id), descendants, Bitmap(0)),
                history=history,
                has_eventless_transitions=has_eventless_transitions,
                after_triggers=after_triggers)

            if state.stable:
                self.stable_bitmap |= bit(state_id)

            # print("state:", full_name)
            # print("ancestors:", len(ancestors))

        init_state(root, "", [])
        self.root = root

        for t in self.transition_list:
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

            t.gen = TransitionOptimization(
                lca=lca,
                arena_bitmap=lca.gen.descendant_bitmap | lca.gen.state_id_bitmap)
