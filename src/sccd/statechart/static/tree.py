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

        self.opt: Optional['StateOptimization'] = None

        if self.parent is not None:
            self.parent.children.append(self)

    # Subset of descendants that are always entered when this state is the target of a transition, minus history states.
    def _effective_targets(self) -> Bitmap:
        if self.default_state:
            # this state + recursion on 'default state'
            return self.opt.state_id_bitmap | self.default_state._effective_targets() 
        else:
            # only this state
            return self.opt.state_id_bitmap

    # States that are always entered when this state is part of the "enter path", but not the actual target of a transition.
    def _additional_effective_targets(self, exclude: 'State') -> Tuple[Bitmap, List['HistoryState']]:
        return self.opt.state_id_bitmap # only this state

    def __repr__(self):
        return "State(\"%s\")" % (self.short_name)

class HistoryState(State):
    __slots__ = ["history_id"]

    def __init__(self, short_name: str, parent: Optional['State']):
        super().__init__(short_name, parent)

        self.history_id: Optional[int] = None

    # # Set of states that may be history values.
    # @abstractmethod
    # def history_mask(self) -> Bitmap:
    #     pass

    def _effective_targets(self) -> Bitmap:
        return Bitmap()

    def _additional_effective_targets(self, exclude: 'State') -> Bitmap:
        assert False # history state cannot have children and therefore should never occur in a "enter path"

class ShallowHistoryState(HistoryState):

    # def history_mask(self) -> Bitmap:
    #     # Only direct children of parent:
    #     return bm_union(s.opt.state_id_bitmap for s in self.parent.children)

    def __repr__(self):
        return "ShallowHistoryState(\"%s\")" % (self.short_name)

class DeepHistoryState(HistoryState):

    def history_mask(self) -> Bitmap:
        # All descendants of parent:
        return self.parent.opt.descendants

    def __repr__(self):
        return "DeepHistoryState(\"%s\")" % (self.short_name)

class ParallelState(State):

    def _effective_targets(self) -> Bitmap:
        # this state + recursive on all children that are not a history state
        return bm_union(c._effective_targets() for c in self.children if not isinstance(c, HistoryState)) | self.opt.state_id_bitmap

    def _additional_effective_targets(self, exclude: 'State') -> Bitmap:
        # 
        return self._effective_targets() & ~exclude._effective_targets()

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
    __slots__ = ["source", "targets", "scope", "target_string", "guard", "actions", "trigger", "opt"]

    def __init__(self, source: State, targets: List[State], scope: Scope, target_string: Optional[str] = None):
        super().__init__()

        self.source: State = source
        self.targets: List[State] = targets
        self.scope: Scope = scope

        self.target_string: Optional[str] = target_string

        self.guard: Optional[Expression] = None
        self.actions: List[Action] = []
        self.trigger: Trigger = _empty_trigger

        self.opt: Optional['TransitionOptimization'] = None        

    def __str__(self):
        return termcolor.colored("%s 🡪 %s" % (self.source.opt.full_name, self.targets[0].opt.full_name), 'green')


# Simply a collection of read-only fields, generated during "optimization" for each state, inferred from the model, i.e. the hierarchy of states and transitions
class StateOptimization(Freezable):
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
class TransitionOptimization(Freezable):
    __slots__ = ["arena", "arena_bitmap", "enter_states_static", "target_history_id", "raised_events"]

    def __init__(self, arena: State, arena_bitmap: Bitmap, enter_states_static: Bitmap, target_history_id: Optional[int], raised_events: Bitmap):
        super().__init__()
        self.arena: State = arena
        self.arena_bitmap: Bitmap = arena_bitmap
        # The "enter set" can be computed partially statically, or entirely statically if there are no history states in it.
        self.enter_states_static: Bitmap = enter_states_static
        self.target_history_id: Optional[int] = target_history_id # History ID if target of transition is a history state, otherwise None.
        self.raised_events: Bitmap = raised_events # (internal) event IDs raised by this transition
        self.freeze()


class StateTree(Freezable):
    __slots__ = ["root", "transition_list", "state_list", "state_dict", "after_triggers", "stable_bitmap", "initial_history_values", "initial_states"]

    def __init__(self, root: State, transition_list: List[Transition], state_list: List[State], state_dict: Dict[str, State], after_triggers: List[AfterTrigger], stable_bitmap: Bitmap, initial_history_values: List[Bitmap], initial_states: Bitmap):
        super().__init__()
        self.root: State = root
        self.transition_list: List[Transition] = transition_list # depth-first document order
        self.state_list: List[State] = state_list # depth-first document order
        self.state_dict: Dict[str, State] = state_dict # mapping from 'full name' to State
        self.after_triggers: List[AfterTrigger] = after_triggers # all after-triggers in the statechart
        self.stable_bitmap: Bitmap = stable_bitmap # set of states that are syntactically marked 'stable'
        self.initial_history_values: List[Bitmap] = initial_history_values # targets of each history state before history has been built.
        self.initial_states: Bitmap = initial_states
        self.freeze()

def optimize_tree(root: State) -> StateTree:
    with timer.Context("optimize tree"):

        def assign_state_id():
            next_id = 0
            def f(state: State, _=None):
                state.opt = StateOptimization()

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

        state_dict = {}
        state_list = []
        stable_bitmap = Bitmap()
        def add_to_list(state: State ,_=None):
            nonlocal stable_bitmap
            state_dict[state.opt.full_name] = state
            state_list.append(state)
            if state.stable:
                stable_bitmap |= state.opt.state_id_bitmap

        transition_list = []
        after_triggers = []
        def visit_transitions(state: State, _=None):
                for t in state.transitions:
                    transition_list.append(t)
                    if t.trigger and isinstance(t.trigger, AfterTrigger):
                        state.opt.after_triggers.append(t.trigger)
                        after_triggers.append(t.trigger)

        def set_ancestors(state: State, ancestors=Bitmap()):
            state.opt.ancestors = ancestors
            return ancestors | state.opt.state_id_bitmap

        def set_descendants(state: State, children_descendants):
            descendants = bm_union(children_descendants)
            state.opt.descendants = descendants
            return state.opt.state_id_bitmap | descendants

        def calculate_effective_targets(state: State, _=None):
            # implementation of "_effective_targets"-method is recursive (slow)
            # store the result, it is always the same:
            state.opt.effective_targets = state._effective_targets()

        initial_history_values = []
        def deal_with_history(state: State, children_history):
            for h in children_history:
                if isinstance(h, DeepHistoryState):
                    state.opt.deep_history = (h.history_id, h.history_mask())
                elif isinstance(h, ShallowHistoryState):
                    state.opt.shallow_history = h.history_id

            if isinstance(state, HistoryState):
                state.history_id = len(initial_history_values)
                initial_history_values.append(state.parent._effective_targets())
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

        visit_tree(root, lambda s: s.children,
            after_children=[
                deal_with_history,
                freeze,
            ])

        for t in transition_list:
            # Arena can be computed statically. First compute Lowest-common ancestor:
            # Intersection between source & target ancestors, last member in depth-first sorted state list.
            lca_id = bm_highest_bit(t.source.opt.ancestors & t.targets[0].opt.ancestors)
            lca = state_list[lca_id]
            arena = lca
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
            enter_path = (t.targets[0].opt.state_id_bitmap | t.targets[0].opt.ancestors) & arena.opt.descendants
            # All states on the enter path will be entered, but on the enter path, there may also be AND-states whose children are not on the enter path, but should also be entered.
            enter_path_iter = bm_items(enter_path)
            state_id = next(enter_path_iter, None)
            enter_states_static = Bitmap()
            while state_id is not None:
                state = state_list[state_id]
                next_state_id = next(enter_path_iter, None)
                if next_state_id:
                    # an intermediate state on the path from arena to target
                    next_state = state_list[next_state_id]
                    enter_states_static |= state._additional_effective_targets(next_state)
                else:
                    # the actual target of the transition
                    enter_states_static |= state.opt.effective_targets
                state_id = next_state_id

            target_history_id = None
            if isinstance(t.targets[0], HistoryState):
                target_history_id = t.targets[0].history_id


            raised_events = Bitmap()
            for a in t.actions:
                if isinstance(a, RaiseInternalEvent):
                    raised_events |= bit(a.event_id)

            t.opt = TransitionOptimization(
                arena=arena,
                arena_bitmap=arena.opt.descendants | arena.opt.state_id_bitmap,
                enter_states_static=enter_states_static,
                target_history_id=target_history_id,
                raised_events=raised_events)

            t.freeze()

        initial_states = root._effective_targets()

        return StateTree(root, transition_list, state_list, state_dict, after_triggers, stable_bitmap, initial_history_values, initial_states)


def priority_source_parent(tree: StateTree) -> List[Transition]:
    # Tree's transition list already ordered parent-first
    return tree.transition_list

# The following 3 priority implementations all do a stable sort with a partial order-key

def priority_source_child(tree: StateTree) -> List[Transition]:
    return sorted(tree.transition_list, key=lambda t: -t.source.opt.depth)

def priority_arena_parent(tree: StateTree) -> List[Transition]:
    return sorted(tree.transition_list, key=lambda t: t.opt.arena.opt.depth)

def priority_arena_child(tree: StateTree) -> List[Transition]:
    return sorted(tree.transition_list, key=lambda t: -t.opt.arena.opt.depth)


def concurrency_arena_orthogonal(tree: StateTree):
    with timer.Context("concurrency_arena_orthogonal"):
        import collections
        # arena_to_transition = collections.defaultdict(list)
        # for t in tree.transition_list:
        #     arena_to_transition[t.opt.arena].append(t)

        # def sets(state: State):
        #     sets = []
        #     for t in arena_to_transition[state]:
        #         sets.append(set((t,)))

        #     for c in state.children:

        #     return sets


        # s = sets(tree.root)

        # print(s)

        sets = {}
        unique_sets = []
        for t1, t2 in itertools.combinations(tree.transition_list, r=2):
            if not (t1.opt.arena_bitmap & t2.opt.arena_bitmap):
                if t1 in sets:
                    sets[t1].add(t2)
                    sets[t2] = sets[t1]
                elif t2 in sets:
                    sets[t2].add(t1)
                    sets[t1] = sets[t2]
                else:
                    s = set((t1,t2))
                    sets[t1] = s
                    sets[t2] = s
                    unique_sets.append(s)
                    print('added', s)
                    

        print((unique_sets))

        # concurrent_set = itertools.chain.from_iterable(itertools.combinations(ls,r) for r in range(len(ls)+1))
        # print(concurrent_set)

        # import collections
        # nonoverlapping = collections.defaultdict(list)
        # for t1,t2 in itertools.combinations(tree.transition_list, r=2):
        #     if not (t1.opt.arena_bitmap & t2.opt.arena_bitmap):
        #         nonoverlapping[t1].append(t2)
        #         nonoverlapping[t2].append(t1)

        # for t, ts in nonoverlapping.items():
        #     print(str(t), "does not overlap with", ",".join(str(t) for t in ts))

        # print(len(nonoverlapping), "nonoverlapping pairs of transitions")

def concurrency_src_dst_orthogonal(tree: StateTree):
    with timer.Context("concurrency_src_dst_orthogonal"):
        import collections
        nonoverlapping = collections.defaultdict(list)
        for t1,t2 in itertools.combinations(tree.transition_list, r=2):
            lca_src = tree.state_list[bm_highest_bit(t1.source.opt.ancestors & t2.source.opt.ancestors)]
            lca_dst = tree.state_list[bm_highest_bit(t1.targets[0].opt.ancestors & t2.targets[0].opt.ancestors)]
            if isinstance(lca_src, ParallelState) and isinstance(lca_dst, ParallelState):
                nonoverlapping[t1].append(t2)
                nonoverlapping[t2].append(t1)

        for t, ts in nonoverlapping.items():
            print(str(t), "does not overlap with", ",".join(str(t) for t in ts))

        print(len(nonoverlapping), "nonoverlapping pairs of transitions")
