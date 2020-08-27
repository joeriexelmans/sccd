from sccd.common.exceptions import *
from sccd.statechart.static.tree import StateTree, Transition, State, ParallelState
from sccd.util.graph import strongly_connected_components
from typing import *
from sccd.util.visit_tree import visit_tree
from sccd.util.bitmap import *
import collections
import itertools

EdgeList = List[Tuple[Transition,Transition]]

# explicit ordering of orthogonal regions
def ooss_explicit_ordering(tree: StateTree) -> EdgeList:
    edges: EdgeList = []
    # get all outgoing transitions of state or one of its descendants
    def get_transitions(s: State) -> List[Transition]:
        transitions = []
        def visit_state(s: State, _=None):
            transitions.extend(s.transitions)
        visit_tree(s, lambda s: s.children, before_children=[visit_state])
        return transitions
    # create edges between transitions in one region to another
    def visit_parallel_state(s: State, _=None):
        if isinstance(s, ParallelState):
            prev = []
            # s.children are the orthogonal regions in document order
            for region in s.children:
                curr = get_transitions(region)
                if len(curr) > 0: # skip empty regions
                    edges.extend(itertools.product(prev, curr))
                    prev = curr
    visit_tree(tree.root, lambda s: s.children,
        before_children=[visit_parallel_state])
    return edges

# explicit ordering of outgoing transitions of the same state
def explicit(tree: StateTree) -> EdgeList:
    edges: EdgeList = []
    def visit_state(s: State, _=None):
        prev = None
        # s.transitions are s' outgoing transitions in document order
        for t in s.transitions:
            if prev is not None:
                edges.append((prev, t))
            prev = t
    visit_tree(tree.root, lambda s: s.children,
        before_children=[visit_state])
    return edges

# hierarchical Source-Parent ordering
def source_parent(tree: StateTree) -> EdgeList:
    edges: EdgeList = []
    def visit_state(s: State, parent_transitions: List[Transition] = []) -> List[Transition]:
        if len(s.transitions) > 0: # skip states without transitions
            edges.extend(itertools.product(parent_transitions, s.transitions))
            return s.transitions
        return parent_transitions
    visit_tree(tree.root, lambda s: s.children, before_children=[visit_state])
    return edges

# hierarchical Source-Child ordering
def source_child(tree: StateTree) -> EdgeList:
    edges: EdgeList = []
    def visit_state(s: State, ts: List[List[Transition]]) -> List[Transition]:
        children_transitions = list(itertools.chain.from_iterable(ts))
        if len(s.transitions) > 0: # skip states without transitions
            edges.extend(itertools.product(children_transitions, s.transitions))
            return s.transitions
        else:
            return children_transitions
    visit_tree(tree.root, lambda s: s.children, after_children=[visit_state])
    return edges

# hierarchical Arena-Parent ordering
def arena_parent(tree: StateTree) -> EdgeList:
    edges: EdgeList = []
    partitions = collections.defaultdict(list) # mapping of transition's arena depth to list of transitions
    for t in tree.transition_list:
        partitions[t.opt.arena.opt.depth].append(t)
    ordered_partitions = sorted(partitions.items(), key=lambda tup: tup[0])
    prev = []
    for depth, curr in ordered_partitions:
        edges.extend(itertools.product(prev, curr))
        prev = curr
    return edges

# hierarchical Arena-Child ordering
def arena_child(tree: StateTree) -> EdgeList:
    edges: EdgeList = []
    partitions = collections.defaultdict(list) # mapping of transition's arena depth to list of transitions
    for t in tree.transition_list:
        partitions[t.opt.arena.opt.depth].append(t)
    ordered_partitions = sorted(partitions.items(), key=lambda tup: -tup[0])
    prev = []
    for depth, curr in ordered_partitions:
        edges.extend(itertools.product(prev, curr))
        prev = curr
    return edges

# no priority
def none(tree: StateTree) -> EdgeList:
    return []

# Apply the graph-yielding functions to the given statetree, and merge their results into a single graph
def get_graph(tree: StateTree, *priorities: Callable[[StateTree], EdgeList]) -> EdgeList:
    edges = list(itertools.chain.from_iterable(p(tree) for p in priorities))
    return edges

# Checks whether the 'priorities' given yield a valid ordering of transitions in the statechart.
# Returns list of all transitions in statechart, ordered by priority (high -> low).
def get_total_ordering(tree: StateTree, *priorities: Callable[[StateTree], EdgeList]) -> List[Transition]:
    # "edges" is a list of pairs (t1, t2) of transitions, where t1 has higher priority than t2.
    edges = get_graph(tree, *priorities)
    scc = strongly_connected_components(edges)
    if len(scc) != len(tree.transition_list):
        # Priority graph contains cycles
        for component in scc:
            if len(component) > 1:
                raise ModelStaticError("Cycle among transition priorities: " + str(component))

    total_ordering = []

    # Raises an exception if the given set of transitions can potentially be enabled simulatenously, wrt. their source states in the state tree.
    def check_unordered(transitions):
        pairs = itertools.combinations(transitions, 2)
        for t1, t2 in pairs:
            # LCA of their sources
            lca_id = bm_highest_bit(t1.source.opt.ancestors & t2.source.opt.ancestors)
            lca = tree.state_list[lca_id]
            # Transitions are orthogonal to each other (LCA is And-state):
            if isinstance(lca, ParallelState):
                raise ModelStaticError("Nondeterminism! No priority between orthogonal transitions: %s, %s" % (t1, t2))
            # They have the same source:
            if t1.source is t2.source:
                raise ModelStaticError("Nondeterminism! No priority between outgoing transitions of same state: %s, %s" % (t1, t2))
            # Their source states are ancestors of one another:
            if bm_has(t1.source.opt.ancestors, t2.source.opt.state_id) or bm_has(t2.source.opt.ancestors, t1.source.opt.state_id):
                raise ModelStaticError("Nondeterminism! No priority between ancestral transitions: %s, %s" % (t1, t2))

    remaining_transitions = set(tree.transition_list)
    remaining_edges = edges
    while len(remaining_edges) > 0:
        # 1. Find set of highest-priority transitions (= the ones that have no incoming edges)
        # Such a set must exist, because we've already assured that are no cycles in the graph.
        highs = set() # all transitions that have outgoing edges ("higher priority")
        lows = set() # all transitions that have incoming edges ("lower priority")
        for high, low in remaining_edges:
            highs.add(high)
            lows.add(low)
        highest_priority = highs - lows
        # 2. Check if the transitions in this set are allowed to have equal priority.
        check_unordered(highest_priority) # may raise Exception
        # 3. All good. Add the transitions in the highest-priority set in any order to the total ordering
        total_ordering.extend(highest_priority)
        # 4. Remove the transitions of the highest-priority set from the graph, and repeat.
        remaining_edges = [(high,low) for high, low in remaining_edges if high not in highest_priority]
        remaining_transitions -= highest_priority

    # Finally, there may be transitions that occur in the priority graph only as vertices, e.g. in flat statecharts:
    check_unordered(remaining_transitions)
    total_ordering.extend(remaining_transitions)

    return total_ordering
