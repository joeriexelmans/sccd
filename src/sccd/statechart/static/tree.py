import termcolor
from typing import *
from sccd.statechart.static.action import *
from sccd.util.bitmap import *


@dataclass
class State:
    short_name: str # value of 'id' attribute in XML
    parent: Optional['State'] # only None if root state
    # scope: Scope # states have their own scope: variables can be declared in <onentry>, subsequently read in guard conditions and actions.

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
            return self.name + '(' + ', '.join(p.render() for p in self.params_decl) + ')'
        else:
            return self.name

@dataclass
class Trigger:
    enabling: List[EventDecl]

    def __post_init__(self):
        # Optimization: Require 'enabling' to be sorted!
        assert sorted(self.enabling, key=lambda e: e.id) == self.enabling

        self.enabling_bitmap = Bitmap.from_list(e.id for e in self.enabling)

    def check(self, events_bitmap: Bitmap) -> bool:
        return (self.enabling_bitmap & events_bitmap) == self.enabling_bitmap

    def render(self) -> str:
        return ' ∧ '.join(e.render() for e in self.enabling)

    def copy_params_to_stack(self, ctx: EvalContext):
        # Both 'ctx.events' and 'self.enabling' are sorted by event ID,
        # this way we have to iterate over each of both lists at most once.
        iterator = iter(self.enabling)
        try:
            event_decl = next(iterator)
            offset = 0
            for e in ctx.events:
                if e.id < event_decl.id:
                    continue
                else:
                    while e.id > event_decl.id:
                        event_decl = next(iterator)
                    for p in e.params:
                        ctx.memory.store(offset, p)
                        offset += 1
        except StopIteration:
            pass

@dataclass
class NegatedTrigger(Trigger):
    disabling: List[EventDecl]

    def __post_init__(self):
        Trigger.__post_init__(self)
        self.disabling_bitmap = Bitmap.from_list(e.id for e in self.disabling)

    def check(self, events_bitmap: Bitmap) -> bool:
        return Trigger.check(self, events_bitmap) and not (self.disabling_bitmap & events_bitmap)

    def render(self) -> str:
        return Trigger.render(self) + ' ∧ ' + ' ∧ '.join('¬'+e.render() for e in self.disabling)

class AfterTrigger(Trigger):
    def __init__(self, id: int, name: str, after_id: int, delay: Expression):
        enabling = [EventDecl(id=id, name=name, params_decl=[])]
        super().__init__(enabling)

        self.id = id
        self.name = name
        self.after_id = after_id # unique ID for AfterTrigger
        self.delay = delay

    def render(self) -> str:
        return "after("+self.delay.render()+")"

    # An 'after'-event also has 1 parameter, but it is not accessible to the user,
    # hence the override.
    def copy_params_to_stack(self, ctx: EvalContext):
        pass

@dataclass
class Transition:
    source: State
    targets: List[State]
    scope: Scope

    target_string: Optional[str] = None

    guard: Optional[Expression] = None
    actions: List[Action] = field(default_factory=list)
    trigger: Optional[Trigger] = None

    gen: Optional['TransitionOptimization'] = None        
                    
    def __repr__(self):
        return termcolor.colored("%s 🡪 %s" % (self.source.gen.full_name, self.targets[0].gen.full_name), 'green')

# Generated fields (for optimization) of a transition
@dataclass(frozen=True)
class TransitionOptimization:
    lca: State
    lca_bitmap: Bitmap
    arena: State
    arena_bitmap: Bitmap

# @dataclass
class StateTree:

    # root: The root state of a state,transition tree structure with with all fields filled in,
    #       except the 'gen' fields. This function will fill in the 'gen' fields.
    def __init__(self, root: State, after_triggers: List[AfterTrigger]):
        self.state_dict = {} # mapping from 'full name' to State
        self.state_list = [] # depth-first list of states
        self.transition_list = [] # all transitions in the tree, sorted by source state, depth-first
        self.after_triggers = after_triggers
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
                    # self.after_triggers.append(t.trigger)

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

            arena = lca
            while isinstance(arena, ParallelState):
                arena = arena.parent

            t.gen = TransitionOptimization(
                lca=lca,
                lca_bitmap=lca.gen.descendant_bitmap | lca.gen.state_id_bitmap,
                arena=arena,
                arena_bitmap=arena.gen.descendant_bitmap | arena.gen.state_id_bitmap)
