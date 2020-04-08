import termcolor
from typing import *
from sccd.statechart.static.action import *
from sccd.util.bitmap import *
from sccd.util import timer
from sccd.util.visit_tree import *

@dataclass
class State:
    short_name: str # value of 'id' attribute in XML
    parent: Optional['State'] # only None if root state
    # scope: Scope # states have their own scope: variables can be declared in <onentry>, subsequently read in guard conditions and actions.

    stable: bool = False # whether this is a stable stabe. this field is ignored if maximality semantics is not set to SYNTACTIC

    children: List['State'] = field(default_factory=list)
    default_state: 'State' = None # child state pointed to by 'initial' attribute

    transitions: List['Transition'] = field(default_factory=list)

    enter: List[Action] = field(default_factory=list)
    exit: List[Action] = field(default_factory=list)

    opt: Optional['StateOptimization'] = None

    def __post_init__(self):
        if self.parent is not None:
            self.parent.children.append(self)

    def target_states(self, instance) -> Bitmap:
        return self.opt.ts_static | functools.reduce(lambda x,y: x|y, (s.target_states(instance) for s in self.opt.ts_dynamic), Bitmap())

    def additional_target_states(self, instance) -> Bitmap:
        return self.opt.state_id_bitmap

    def __repr__(self):
        return "State(\"%s\")" % (self.opt.full_name)

# Generated fields (for optimization) of a state
@dataclass
class StateOptimization:
    full_name: str = ""

    state_id: int = -1
    state_id_bitmap: Bitmap = Bitmap() # bitmap with only state_id-bit set

    ancestors: Bitmap = Bitmap()
    descendants: Bitmap = Bitmap()

    # subset of children that are HistoryState
    history: List[Tuple[State, Bitmap]] = field(default_factory=list)

    # Subset of descendants that are always entered when this state is the target of a transition
    ts_static: Bitmap = Bitmap() 
    # Subset of descendants that MAY be entered when this state is the target of a transition, depending on the history values.
    ts_dynamic: List[State] = field(default_factory=list) 

    # Triggers of outgoing transitions that are AfterTrigger.
    after_triggers: List['AfterTrigger'] = field(default_factory=list)

class HistoryState(State):
    # Set of states that may be history values.
    @abstractmethod
    def history_mask(self) -> Bitmap:
        pass

    def target_states(self, instance) -> Bitmap:
        try:
            return instance.history_values[self.opt.state_id]
        except KeyError:
            # Parent's target states, but not the parent itself:
            return self.parent.target_states(instance) & ~self.parent.opt.state_id_bitmap

    def additional_target_states(self, instance) -> Bitmap:
        return Bitmap()

class ShallowHistoryState(HistoryState):

    def history_mask(self) -> Bitmap:
        # Only direct children of parent:
        return states_to_bitmap(self.parent.children)

    def __repr__(self):
        return "ShallowHistoryState(\"%s\")" % (self.opt.full_name)

class DeepHistoryState(HistoryState):

    def history_mask(self) -> Bitmap:
        # All descendants of parent:
        return self.parent.opt.descendants

    def __repr__(self):
        return "DeepHistoryState(\"%s\")" % (self.opt.full_name)

class ParallelState(State):

    def additional_target_states(self, instance) -> Bitmap:
        return self.target_states(instance)

    def __repr__(self):
        return "ParallelState(\"%s\")" % (self.opt.full_name)

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

    # Override.
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

    opt: Optional['TransitionOptimization'] = None        
                    
    def __repr__(self):
        return termcolor.colored("%s 🡪 %s" % (self.source.opt.full_name, self.targets[0].opt.full_name), 'green')

# Generated fields (for optimization) of a transition
@dataclass(frozen=True)
class TransitionOptimization:
    arena: State
    arena_bitmap: Bitmap

# Reduce a list of states to a set of states, as a bitmap
def states_to_bitmap(state_list: List[State]) -> Bitmap:
    return reduce(lambda x,y: x|y, (s.opt.state_id_bitmap for s in state_list), Bitmap())


# @dataclass
class StateTree:

    # root: The root state of a state,transition tree structure with with all fields filled in,
    #       except the 'gen' fields. This function will fill in the 'gen' fields.
    def __init__(self, root: State):
        timer.start("optimize tree")

        self.root = root

        self.transition_list = []
        self.after_triggers = []
        def init_opt():
            next_id = 0
            def f(state: State, _=None):
                state.opt = StateOptimization()

                nonlocal next_id
                state.opt.state_id = next_id
                state.opt.state_id_bitmap = bit(next_id)
                next_id += 1

                for t in state.transitions:
                    self.transition_list.append(t)
                    if t.trigger and isinstance(t.trigger, AfterTrigger):
                        state.opt.after_triggers.append(t.trigger)
                        self.after_triggers.append(t.trigger)
            return f

        def assign_full_name(state: State, parent_full_name: str = ""):
            if state is root:
                full_name = '/'
            elif state.parent is root:
                full_name = '/' + state.short_name
            else:
                full_name = parent_full_name + '/' + state.short_name
            state.opt.full_name = full_name
            return full_name

        self.state_dict = {}
        self.state_list = []
        self.stable_bitmap = Bitmap()
        def add_to_list(state: State ,_=None):
            self.state_dict[state.opt.full_name] = state
            self.state_list.append(state)
            if state.stable:
                self.stable_bitmap |= state.opt.state_id_bitmap

        def set_ancestors(state: State, ancestors=[]):
            state.opt.ancestors = states_to_bitmap(ancestors)
            return ancestors + [state]

        def set_descendants(state: State, children_descendants):
            descendants = reduce(lambda x,y: x|y, children_descendants, Bitmap())
            state.opt.descendants = descendants
            return state.opt.state_id_bitmap | descendants

        def set_static_target_states(state: State, _):
            if isinstance(state, ParallelState):
                state.opt.ts_static = reduce(lambda x,y: x|y, (s.opt.ts_static for s in state.children), state.opt.state_id_bitmap)
                state.opt.ts_dynamic = list(itertools.chain.from_iterable(c.opt.ts_dynamic for c in state.children if not isinstance(c, HistoryState)))
            elif isinstance(state, HistoryState):
                state.opt.ts_static = Bitmap()
                state.opt.ts_dynamic = state.children
            else: # "regular" state:
                if state.default_state:
                    state.opt.ts_static = state.opt.state_id_bitmap | state.default_state.opt.ts_static
                    state.opt.ts_dynamic = state.default_state.opt.ts_dynamic
                else:
                    state.opt.ts_static = state.opt.state_id_bitmap
                    state.opt.ts_dynamic = []

        def add_history(state: State, _= None):
            for c in state.children:
                if isinstance(c, HistoryState):
                    state.opt.history.append((c, c.history_mask()))

        visit_tree(root, lambda s: s.children,
            before_children=[
                init_opt(),
                assign_full_name,
                add_to_list,
                set_ancestors,
            ],
            after_children=[
                set_descendants,
                add_history,
                set_static_target_states,
            ])


        for t in self.transition_list:
            # intersection between source & target ancestors, last member in depth-first sorted state list.
            lca_id = (t.source.opt.ancestors & t.targets[0].opt.ancestors).highest_bit()
            lca = self.state_list[lca_id]
            arena = lca
            while isinstance(arena, (ParallelState, HistoryState)):
                arena = arena.parent

            t.opt = TransitionOptimization(
                arena=arena,
                arena_bitmap=arena.opt.descendants | arena.opt.state_id_bitmap)

        timer.stop("optimize tree")
