import termcolor
from typing import *
import itertools
from sccd.statechart.static.action import *
from sccd.util.bitmap import *
from sccd.util import timer
from sccd.util.visit_tree import *
from sccd.util.freezable import *

class State(Freezable):
    __slots__ = ["short_name", "parent", "stable", "children", "default_state", "transitions", "enter", "exit", "opt"]

    def __init__(self, short_name: str, parent: Optional['State']):
        super().__init__()

        self.short_name: str = short_name # value of 'id' attribute in XML
        self.parent: Optional['State'] = parent # only None if root state

        self.stable: bool = False # whether this is a stable stabe. this field is ignored if maximality semantics is not set to SYNTACTIC

        self.children: List['State'] = []
        self.default_state: 'State' = None # child state pointed to by 'initial' attribute

        self.transitions: List['Transition'] = []

        self.enter: List[Action] = []
        self.exit: List[Action] = []

        # Statically computed stuff from tree structure:
        self.opt: Optional['StateStatic'] = None

        if self.parent is not None:
            self.parent.children.append(self)

    # Subset of descendants that are always entered when this state is the target of a transition, minus history states. Recursive implementation, so better to use self.opt.effective_targets, which is computed statically
    def effective_targets(self) -> List['State']:
        if self.default_state:
            # or-state: this state + recursion on 'default state'
            return [self] + self.default_state.effective_targets()
        else:
            # basic state
            return [self]

    # States that are always entered when this state is part of the "enter path", but not the actual target of a transition.
    def additional_effective_targets(self, exclude: 'State') -> List['State']:
        return [self]

    def __repr__(self):
        return "State(\"%s\")" % (self.short_name)

class HistoryState(State):
    __slots__ = ["history_id"]

    def __init__(self, short_name: str, parent: Optional['State']):
        super().__init__(short_name, parent)

    def effective_targets(self) -> List['State']:
        return []

    def additional_effective_targets(self, exclude: 'State') -> List['State']:
        assert False # history state cannot have children and therefore should never occur in a "enter path"

class ShallowHistoryState(HistoryState):

    def __repr__(self):
        return "ShallowHistoryState(\"%s\")" % (self.short_name)

class DeepHistoryState(HistoryState):

    def __repr__(self):
        return "DeepHistoryState(\"%s\")" % (self.short_name)

class ParallelState(State):

    def effective_targets(self) -> List['State']:
        # this state + recursive on all children that are not a history state
        return self.additional_effective_targets(exclude=None)

    def additional_effective_targets(self, exclude: 'State') -> List['State']:
        # this state + all effective targets of children, except for 'excluded state' and history states
        return [self] + list(itertools.chain(*(c.effective_targets() for c in self.children if not isinstance(c, HistoryState) and c is not exclude)))

    def __repr__(self):
        return "ParallelState(\"%s\")" % (self.short_name)

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

_empty_trigger = Trigger(enabling=[])

class Transition(Freezable):
    __slots__ = ["source", "target", "scope", "target_string", "guard", "actions", "trigger", "opt"]

    def __init__(self, source: State, target: State, scope: Scope, target_string: Optional[str] = None):
        super().__init__()

        self.source: State = source
        self.target: State = target
        self.scope: Scope = scope

        self.target_string: Optional[str] = target_string

        self.guard: Optional[Expression] = None
        self.actions: List[Action] = []
        self.trigger: Trigger = _empty_trigger

        # Statically computed stuff from tree structure:
        self.opt: Optional['TransitionStatic'] = None        

    def __str__(self):
        return termcolor.colored("%s 🡪 %s" % (self.source.opt.full_name, self.target.opt.full_name), 'green')

    __repr__ = __str__


# Simply a collection of read-only fields, generated during "optimization" for each state, inferred from the model, i.e. the hierarchy of states and transitions
class StateStatic(Freezable):
    __slots__ = ["full_name", "depth", "state_id", "state_id_bitmap", "ancestors", "descendants", "effective_targets", "deep_history", "shallow_history", "after_triggers"]
    def __init__(self):
        super().__init__()

        self.full_name: str = ""

        self.depth: int -1 # Root is 0, root's children are 1, and so on
        self.state_id: int = -1
        self.state_id_bitmap: Bitmap = Bitmap() # bitmap with only state_id-bit set

        self.ancestors: Bitmap = Bitmap()
        self.descendants: Bitmap = Bitmap()

        self.effective_targets: Bitmap = Bitmap()

        # If a direct child of this state is a deep history state, then "deep history" needs to be recorded when exiting this state. This value contains a tuple, with the (history-id, history_mask) of that child state.
        self.deep_history: Optional[Tuple[int, Bitmap]] = None

        # If a direct child of this state is a shallow history state, then "shallow history" needs to be recorded when exiting this state. This value is the history-id of that child state
        self.shallow_history: Optional[int] = None

        # Triggers of outgoing transitions that are AfterTrigger.
        self.after_triggers: List[AfterTrigger] = []


# Data that is generated for each transition.
class TransitionStatic(Freezable):
    __slots__ = ["exit_mask", "arena_bitmap", "enter_states_static", "target_history_id", "target_stable", "raised_events"]

    def __init__(self, exit_mask: Bitmap, arena_bitmap: Bitmap, enter_states_static: Bitmap, target_history_id: Optional[int], target_stable: bool, raised_events: Bitmap):
        super().__init__()
        self.exit_mask: State = exit_mask
        self.arena_bitmap: Bitmap = arena_bitmap
        # The "enter set" can be computed partially statically, or entirely statically if there are no history states in it.
        self.enter_states_static: Bitmap = enter_states_static
        self.target_history_id: Optional[int] = target_history_id # History ID if target of transition is a history state, otherwise None.
        self.target_stable: bool = target_stable # Whether target state is a stable state
        self.raised_events: Bitmap = raised_events # (internal) event IDs raised by this transition
        self.freeze()


class StateTree(Freezable):
    __slots__ = ["root", "transition_list", "state_list", "state_dict", "timer_count", "initial_history_values", "initial_states"]

    def __init__(self, root: State):
        super().__init__()
        self.root: State = root

        self.state_dict = {}
        self.state_list = []
        self.transition_list = []
        self.timer_count = 0 # number of after-transitions in the statechart
        self.initial_history_values = []

        with timer.Context("optimize tree"):

            def assign_state_id():
                next_id = 0
                def f(state: State, _=None):
                    state.opt = StateStatic()

                    nonlocal next_id
                    state.opt.state_id = next_id
                    state.opt.state_id_bitmap = bit(next_id)
                    next_id += 1

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

            def assign_depth(state: State, parent_depth: int = 0):
                state.opt.depth = parent_depth + 1
                return parent_depth + 1

            def add_to_list(state: State ,_=None):
                self.state_dict[state.opt.full_name] = state
                self.state_list.append(state)

            def visit_transitions(state: State, _=None):
                    for t in state.transitions:
                        self.transition_list.append(t)
                        if t.trigger and isinstance(t.trigger, AfterTrigger):
                            state.opt.after_triggers.append(t.trigger)
                            self.timer_count += 1

            def set_ancestors(state: State, ancestors=Bitmap()):
                state.opt.ancestors = ancestors
                return ancestors | state.opt.state_id_bitmap

            def set_descendants(state: State, children_descendants):
                descendants = bm_union(children_descendants)
                state.opt.descendants = descendants
                return state.opt.state_id_bitmap | descendants

            def calculate_effective_targets(state: State, _=None):
                # implementation of "effective_targets"-method is recursive (slow)
                # store the result, it is always the same:
                state.opt.effective_targets = states_to_bitmap(state.effective_targets())

            history_ids = {}
            def deal_with_history(state: State, children_history):
                for h in children_history:
                    if isinstance(h, DeepHistoryState):
                        state.opt.deep_history = (history_ids[h], h.parent.opt.descendants)
                    elif isinstance(h, ShallowHistoryState):
                        state.opt.shallow_history = history_ids[h]

                if isinstance(state, HistoryState):
                    history_ids[state] = len(self.initial_history_values) # generate history ID
                    self.initial_history_values.append(state.parent.opt.effective_targets)
                    return state

            def freeze(state: State, _=None):
                state.freeze()
                state.opt.freeze()

            visit_tree(root, lambda s: s.children,
                before_children=[
                    assign_state_id(),
                    assign_full_name,
                    assign_depth,
                    add_to_list,
                    visit_transitions,
                    set_ancestors,
                ],
                after_children=[
                    set_descendants,
                    calculate_effective_targets,
                ])

            self.initial_states = root.opt.effective_targets

            visit_tree(root, lambda s: s.children,
                after_children=[
                    deal_with_history,
                    freeze,
                ])

            for t in self.transition_list:
                # Arena can be computed statically. First compute Lowest-common ancestor:
                arena = self.lca(t.source, t.target)
                # Arena must be an Or-state:
                while isinstance(arena, (ParallelState, HistoryState)):
                    arena = arena.parent

                # Exit states can be efficiently computed at runtime based on the set of current states.
                # Enter states are more complex but luckily, can be computed *partially* statically:

                # As a start, we calculate the enter path:
                # The enter path is the path from arena to the target state (not including the arena state itself).
                # Enter path is the intersection between:
                #   1) the transition's target and its ancestors, and
                #   2) the arena's descendants
                enter_path = (t.target.opt.state_id_bitmap | t.target.opt.ancestors) & arena.opt.descendants
                # All states on the enter path will be entered, but on the enter path, there may also be AND-states whose children are not on the enter path, but should also be entered.
                enter_path_iter = self.bitmap_to_states(enter_path)
                entered_state = next(enter_path_iter, None)
                enter_states_static = Bitmap()
                while entered_state is not None:
                    next_entered_state = next(enter_path_iter, None)
                    if next_entered_state:
                        # an intermediate state on the path from arena to target
                        enter_states_static |= states_to_bitmap(entered_state.additional_effective_targets(next_entered_state))
                    else:
                        # the actual target of the transition
                        enter_states_static |= entered_state.opt.effective_targets
                    entered_state = next_entered_state

                target_history_id = None
                if isinstance(t.target, HistoryState):
                    target_history_id = history_ids[t.target]

                raised_events = Bitmap()
                for a in t.actions:
                    if isinstance(a, RaiseInternalEvent):
                        raised_events |= bit(a.event_id)

                t.opt = TransitionStatic(
                    exit_mask=arena.opt.descendants,
                    arena_bitmap=arena.opt.descendants | arena.opt.state_id_bitmap,
                    enter_states_static=enter_states_static,
                    target_history_id=target_history_id,
                    target_stable=t.target.stable,
                    raised_events=raised_events)

                t.freeze()

            self.freeze()

    def bitmap_to_states(self, bitmap: Bitmap) -> Iterator[State]:
        return (self.state_list[id] for id in bm_items(bitmap))

    def bitmap_to_states_reverse(self, bitmap: Bitmap) -> Iterator[State]:
        return (self.state_list[id] for id in bm_reverse_items(bitmap))

    def lca(self, s1: State, s2: State) -> State:
        # Intersection between source & target ancestors, last member in depth-first sorted state list.
        return self.state_list[bm_highest_bit(s1.opt.ancestors & s2.opt.ancestors)]

def states_to_bitmap(states: Iterable[State]) -> Bitmap:
    return bm_from_list(s.opt.state_id for s in states)

def is_ancestor(parent: State, child: State) -> bool:
    return bm_has(child.opt.ancestors, parent.opt.state_id)
