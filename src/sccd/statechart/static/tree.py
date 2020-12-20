import termcolor
from typing import *
import itertools
from sccd.statechart.static.action import *
from sccd.util.bitmap import *
from sccd.util import timer
from sccd.util.visit_tree import *
from sccd.util.freezable import *
from abc import *

@dataclass(eq=False)
class AbstractState:
    short_name: str # value of 'id' attribute in XML
    parent: Optional['AbstractState'] # only None if root state
    children: List['AbstractState'] = field(default_factory=list)


    ####### Calculated values below ########

    state_id: int = -1
    state_id_bitmap: Bitmap = Bitmap() # bitmap with only state_id-bit set
    full_name: str = ""
    ancestors: Bitmap = Bitmap()
    descendants: Bitmap = Bitmap()

    effective_targets: Bitmap = Bitmap()

    def __post_init__(self):
        if self.parent is not None:
            self.parent.children.append(self)

    def __str__(self):
        return "AbstractState(%s)" % self.short_name

    __repr__ = __str__

@dataclass(eq=False)
class State(AbstractState, Visitable):
    type: 'StateType' = None

    real_children: List['State'] = field(default_factory=list) # children, but not including pseudo-states such as history

    # whether this is a stable stabe. this field is ignored if maximality semantics is not set to SYNTACTIC
    stable: bool = False

    # Outgoing transitions
    transitions: List['Transition'] = field(default_factory=list)

    enter: List[Action] = field(default_factory=list)
    exit: List[Action] = field(default_factory=list)

    ####### Calculated values below ########

    depth: int = -1 # Root is 0, root's children are 1, and so on

    # If a direct child of this state is a deep history state, then "deep history" needs to be recorded when exiting this state. This value contains a tuple, with the (history-id, history_mask, history state) of that child state.
    deep_history: Optional[Tuple[int, Bitmap, 'DeepHistoryState']] = None

    # If a direct child of this state is a shallow history state, then "shallow history" needs to be recorded when exiting this state. This value is the history-id of that child state
    shallow_history: Optional[Tuple[int, 'ShallowHistoryState']] = None

    # Triggers of outgoing transitions that are AfterTrigger.
    after_triggers: List['AfterTrigger'] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if self.parent is not None:
            self.parent.real_children.append(self)

    def __str__(self):
        if isinstance(self.type, AndState):
            return "AndState(%s)" % self.short_name
        elif isinstance(self.type, OrState):
            return "OrState(%s)" % self.short_name
        else:
            return "State?(%s)" % self.short_name

    __repr__ = __str__


@dataclass(eq=False)
class HistoryState(AbstractState):
    history_id: int = -1

    def __post_init__(self):
        super().__post_init__()
        self.type = HistoryStateType(self)

@dataclass(eq=False)
class ShallowHistoryState(HistoryState):
    def __str__(self):
        return "ShallowHistoryState(%s)" % self.short_name
    __repr__ = __str__


@dataclass(eq=False)
class DeepHistoryState(HistoryState):
    def __str__(self):
        return "DeepHistoryState(%s)" % self.short_name
    __repr__ = __str__

@dataclass(eq=False)
class StateType(ABC):
    state: State

    @abstractmethod
    def effective_targets(self):
        pass

    @abstractmethod
    def additional_effective_targets(self, exclude: 'State'):
        pass

@dataclass(eq=False)
class AndState(StateType):

    def effective_targets(self):
        return self.additional_effective_targets(None)

    def additional_effective_targets(self, exclude: 'State'):
        return [self.state] + list(itertools.chain(*(c.type.effective_targets() for c in self.state.children if not isinstance(c, HistoryState) and c is not exclude)))

@dataclass(eq=False)
class OrState(StateType):
    default_state: AbstractState

    def effective_targets(self):
        return [self.state] + self.default_state.type.effective_targets()

    def additional_effective_targets(self, exclude: 'State'):
        return [self.state]

@dataclass(eq=False)
class HistoryStateType(StateType):

    def effective_targets(self):
        return []

    def additional_effective_targets(self, exclude: 'State'):
        assert False # history state cannot have children and therefore should never occur in a "enter path"

@dataclass
class EventDecl:
    __slots__ = ["id", "name", "params_decl"]

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
    __slots__ = ["enabling", "enabling_bitmap"]

    enabling: List[EventDecl]

    def __post_init__(self):
        # Optimization: Require 'enabling' to be sorted!
        assert sorted(self.enabling, key=lambda e: e.id) == self.enabling

        self.enabling_bitmap = bm_from_list(e.id for e in self.enabling)

    def check(self, events_bitmap: Bitmap) -> bool:
        return (self.enabling_bitmap & events_bitmap) == self.enabling_bitmap

    def render(self) -> str:
        return ' ∧ '.join(e.render() for e in self.enabling)

    def copy_params_to_stack(self, events: List[InternalEvent], memory: MemoryInterface):
        # Both 'events' and 'self.enabling' are sorted by event ID,
        # this way we have to iterate over each of both lists at most once.
        iterator = iter(self.enabling)
        try:
            event_decl = next(iterator)
            offset = 0
            for e in events:
                if e.id < event_decl.id:
                    continue
                else:
                    while e.id > event_decl.id:
                        event_decl = next(iterator)
                    for p in e.params:
                        memory.store(offset, p)
                        offset += 1
        except StopIteration:
            pass

@dataclass
class NegatedTrigger(Trigger):
    __slots__ = ["disabling", "disabling_bitmap"]

    disabling: List[EventDecl]

    def __post_init__(self):
        Trigger.__post_init__(self)
        self.disabling_bitmap = bm_from_list(e.id for e in self.disabling)

    def check(self, events_bitmap: Bitmap) -> bool:
        return Trigger.check(self, events_bitmap) and not (self.disabling_bitmap & events_bitmap)

    def render(self) -> str:
        return ' ∧ '.join(itertools.chain((e.render() for e in self.enabling), ('¬'+e.render() for e in self.disabling)))

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
    def copy_params_to_stack(self, events: List[InternalEvent], memory: MemoryInterface):
        pass

EMPTY_TRIGGER = Trigger(enabling=[])

@dataclass(eq=False)
class Transition:
    source: State
    target_string: Optional[str]
    # scope: Scope

    target: State = None

    guard: Optional[FunctionDeclaration] = None
    actions: List[Action] = field(default_factory=list)
    trigger: Trigger = EMPTY_TRIGGER

    ####### CALCULATED VALUES ########

    id: int = None # just a unique number, >= 0
    exit_mask: State = None
    arena: State = None
    arena_bitmap: Bitmap = None
        # The "enter set" can be computed partially statically, or entirely statically if there are no history states in it.
    enter_states_static: Bitmap = None
    target_history_id: Optional[int] = None # History ID if target of transition is a history state, otherwise None.
    target_stable: bool = None # Whether target state is a stable state
    raised_events: Bitmap = None # (internal) event IDs raised by this transition

    def __str__(self):
        if self.target is None:
            return "Transition(%s -> %s)" % (self.source.short_name, self.target_string)
        else:
            return termcolor.colored("%s -> %s" % (self.source.full_name, self.target.full_name), 'green')

    __repr__ = __str__


class StateTree:
    def __init__(self, root: State):
        super().__init__()
        self.root: State = root

        self.state_dict = {}
        self.state_list = []
        self.transition_list = []
        self.timer_count = 0 # number of after-transitions in the statechart
        self.history_states: List[HistoryState] = []
        self.initial_history_values: List[Bitmap] = []

        with timer.Context("optimize tree"):

            def assign_state_id():
                next_id = 0
                def f(state: State, _=None):
                    nonlocal next_id
                    state.state_id = next_id
                    state.state_id_bitmap = bit(next_id)
                    next_id += 1

                return f

            def assign_full_name(state: State, parent_full_name: str = ""):
                if state is root:
                    full_name = '/'
                elif state.parent is root:
                    full_name = '/' + state.short_name
                else:
                    full_name = parent_full_name + '/' + state.short_name
                state.full_name = full_name
                return full_name

            def assign_depth(state: State, parent_depth: int = 0):
                state.depth = parent_depth + 1
                return parent_depth + 1

            def add_to_list(state: State ,_=None):
                self.state_dict[state.full_name] = state
                self.state_list.append(state)

            def visit_transitions(state: State, _=None):
                    for t in state.transitions:
                        self.transition_list.append(t)
                        if t.trigger and isinstance(t.trigger, AfterTrigger):
                            state.after_triggers.append(t.trigger)
                            self.timer_count += 1

            def set_ancestors(state: State, ancestors=Bitmap()):
                state.ancestors = ancestors
                return ancestors | state.state_id_bitmap

            def set_descendants(state: State, children_descendants):
                descendants = bm_union(children_descendants)
                state.descendants = descendants
                return state.state_id_bitmap | descendants

            def calculate_effective_targets(state: State, _=None):
                # implementation of "effective_targets"-method is recursive (slow)
                # store the result, it is always the same:
                state.effective_targets = states_to_bitmap(state.type.effective_targets())

            def deal_with_history(state: State, children_history):
                for h in children_history:
                    if isinstance(h, DeepHistoryState):
                        state.deep_history = (h.history_id, h.parent.descendants, h)
                    elif isinstance(h, ShallowHistoryState):
                        state.shallow_history = (h.history_id, h)

                if isinstance(state, HistoryState):
                    state.history_id = len(self.initial_history_values) # generate history ID
                    self.history_states.append(state)
                    self.initial_history_values.append(state.parent.effective_targets)
                    return state

            visit_tree(root, lambda s: s.children,
                parent_first=[
                    assign_state_id(),
                    assign_full_name,
                    add_to_list,
                    set_ancestors,
                ],
                child_first=[
                    set_descendants,
                    calculate_effective_targets,
                ])

            visit_tree(root, lambda s: s.real_children,
                parent_first=[
                    assign_depth,
                    visit_transitions,
                ],
                child_first=[])

            self.initial_states = root.effective_targets

            visit_tree(root, lambda s: s.children,
                child_first=[
                    deal_with_history,
                ])

            # print()
            # def pretty_print(s, indent=""):
            #     print(indent, s)
            #     return indent + "  "
            # visit_tree(root, lambda s: s.children,
            #     parent_first=[
            #         pretty_print,
            #     ])

            for t_id, t in enumerate(self.transition_list):
                # Arena can be computed statically. First compute Lowest-common ancestor:
                arena = self.lca(t.source, t.target)
                # Arena must be an Or-state:
                while not isinstance(arena.type, OrState):
                    arena = arena.parent

                # Exit states can be efficiently computed at runtime based on the set of current states.
                # Enter states are more complex but luckily, can be computed *partially* statically:

                # As a start, we calculate the enter path:
                # The enter path is the path from arena to the target state (including the target state, but not including the arena).
                # Enter path is the intersection between:
                #   1) the transition's target and its ancestors, and
                #   2) the arena's descendants
                enter_path = (t.target.state_id_bitmap | t.target.ancestors) & arena.descendants
                # All states on the enter path will be entered, but on the enter path, there may also be AND-states whose children are not on the enter path, but should also be entered.
                enter_path_iter = self.bitmap_to_states(enter_path)
                entered_state = next(enter_path_iter, None)
                enter_states_static = Bitmap()
                while entered_state is not None:
                    next_entered_state = next(enter_path_iter, None)
                    if next_entered_state:
                        # an intermediate state on the path from arena to target
                        enter_states_static |= states_to_bitmap(entered_state.type.additional_effective_targets(next_entered_state))
                    else:
                        # the actual target of the transition
                        enter_states_static |= entered_state.effective_targets
                    entered_state = next_entered_state

                target_history_id = None
                if isinstance(t.target, HistoryState):
                    target_history_id = t.target.history_id

                target_stable = False
                if isinstance(t.target, State):
                    target_stable = t.target.stable

                raised_events = Bitmap()
                for a in t.actions:
                    if isinstance(a, RaiseInternalEvent):
                        raised_events |= bit(a.event_id)

                t.id = t_id
                t.exit_mask = arena.descendants
                t.arena = arena
                t.arena_bitmap = arena.descendants | arena.state_id_bitmap
                t.enter_states_static = enter_states_static
                t.target_history_id = target_history_id
                t.target_stable = target_stable
                t.raised_events = raised_events

    def bitmap_to_states(self, bitmap: Bitmap) -> Iterator[State]:
        return (self.state_list[id] for id in bm_items(bitmap))

    def bitmap_to_states_reverse(self, bitmap: Bitmap) -> Iterator[State]:
        return (self.state_list[id] for id in bm_reverse_items(bitmap))

    def lca(self, s1: State, s2: State) -> State:
        # Intersection between source & target ancestors, last member in depth-first sorted state list.
        return self.state_list[bm_highest_bit(s1.ancestors & s2.ancestors)]

def states_to_bitmap(states: Iterable[State]) -> Bitmap:
    return bm_from_list(s.state_id for s in states)

def is_ancestor(parent: State, child: State) -> bool:
    return bm_has(child.ancestors, parent.state_id)
