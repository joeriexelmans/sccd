from sccd.statechart.static.tree import StateTree, Transition, State, AndState, OrState
from sccd.statechart.static import concurrency
from sccd.statechart.static.semantic_configuration import *
from sccd.util.graph import strongly_connected_components
from typing import *
from sccd.util.visit_tree import visit_tree
from sccd.util.bitmap import *
import collections
import itertools

# Pseudo-vertices reduce the amount of edges in the priority graph
class PseudoVertex:
    pass

Vertex = Union[Transition, PseudoVertex]
EdgeList = List[Tuple[Vertex,Vertex]]

# explicit ordering of orthogonal regions
def explicit_ortho(tree: StateTree) -> EdgeList:
    edges: EdgeList = []
    # get all outgoing transitions of state or one of its descendants
    def get_transitions(s: State) -> List[Transition]:
        transitions = []
        def visit_state(s: State, _=None):
            transitions.extend(s.transitions)
        visit_tree(s, lambda s: s.real_children, parent_first=[visit_state])
        return transitions
    # create edges between transitions in one region to another
    def visit_parallel_state(s: State, _=None):
        if isinstance(s.type, AndState):
            prev = []
            # s.real_children are the orthogonal regions in document order
            for region in s.real_children:
                curr = get_transitions(region)
                if len(curr) > 0: # skip empty regions
                    # instead of creating edges between all transitions in component 'prev' and all transitions in component 'curr' (|prev| x |curr| edges), we add a pseudo-vertex in the graph between them, so we only have to create |prev| + |curr| edges, expressing the same information.
                    if len(prev) > 0:
                        connector = PseudoVertex()
                        edges.extend((t, connector) for t in prev)
                        edges.extend((connector, t) for t in curr)
                    prev = curr
    visit_tree(tree.root, lambda s: s.real_children,
        parent_first=[visit_parallel_state])
    return edges

# explicit ordering of outgoing transitions of the same state
def explicit_same_state(tree: StateTree) -> EdgeList:
    edges: EdgeList = []
    def visit_state(s: State, _=None):
        prev = None
        # s.transitions are s' outgoing transitions in document order
        for t in s.transitions:
            if prev is not None:
                edges.append((prev, t))
            prev = t
    visit_tree(tree.root, lambda s: s.real_children,
        parent_first=[visit_state])
    return edges

# hierarchical Source-Parent ordering
def source_parent(tree: StateTree) -> EdgeList:
    edges: EdgeList = []
    def visit_state(s: State, parent_transitions: List[Transition] = []) -> List[Transition]:
        if len(s.transitions) > 0: # skip states without transitions
            edges.extend(itertools.product(parent_transitions, s.transitions))
            return s.transitions
        return parent_transitions
    visit_tree(tree.root, lambda s: s.real_children, parent_first=[visit_state])
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
    visit_tree(tree.root, lambda s: s.real_children, child_first=[visit_state])
    return edges

# hierarchical Arena-Parent ordering
def arena_parent(tree: StateTree) -> EdgeList:
    edges: EdgeList = []
    partitions = collections.defaultdict(list) # mapping of transition's arena depth to list of transitions
    for t in tree.transition_list:
        partitions[t.arena.depth].append(t)
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
        partitions[t.arena.depth].append(t)
    ordered_partitions = sorted(partitions.items(), key=lambda tup: -tup[0])
    prev = []
    for depth, curr in ordered_partitions:
        edges.extend(itertools.product(prev, curr))
        prev = curr
    return edges

# no priority
def none(tree: StateTree) -> EdgeList:
    return []


# Get the (partial) priority ordering between transitions in the state tree, according to given semantics, as a graph
def get_graph(tree: StateTree, semantics: SemanticConfiguration) -> EdgeList:
    hierarchical = {
        HierarchicalPriority.NONE: none,
        HierarchicalPriority.SOURCE_PARENT: source_parent,
        HierarchicalPriority.SOURCE_CHILD: source_child,
        HierarchicalPriority.ARENA_PARENT: arena_parent,
        HierarchicalPriority.ARENA_CHILD: arena_child,
    }[semantics.hierarchical_priority]

    same_state = {
        SameSourcePriority.NONE: none,
        SameSourcePriority.EXPLICIT: explicit_same_state,
    }[semantics.same_source_priority]

    orthogonal = {
        OrthogonalPriority.NONE: none,
        OrthogonalPriority.EXPLICIT: explicit_ortho,
    }[semantics.orthogonal_priority]

    edges = list(itertools.chain.from_iterable(p(tree) for p in [hierarchical, same_state, orthogonal]))
    return edges

# Checks whether the 'priorities' given yield a valid ordering of transitions in the statechart.
# Returns list of all transitions in statechart, ordered by priority (high -> low).
def generate_total_ordering(tree: StateTree, graph: EdgeList, consistency: concurrency.SmallStepConsistency) -> List[Transition]:
    # "edges" is a list of pairs (t1, t2) of transitions, where t1 has higher priority than t2.
    edges = graph
    scc = strongly_connected_components(edges)
    if len(scc) != len(tree.transition_list):
        # Priority graph contains cycles
        for component in scc:
            if len(component) > 1:
                raise ModelStaticError("Cycle among transition priorities: " + str(component))

    total_ordering = []

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
        # pseudo-vertices filtered from it:
        highest_priority_transitions = set(t for t in highest_priority if not isinstance(t, PseudoVertex))
        # 2. Check if the transitions in this set are allowed to have equal priority.
        concurrency.check_nondeterminism(tree, highest_priority_transitions, consistency) # may raise Exception
        # 3. All good. Add the transitions in the highest-priority set in any order to the total ordering
        total_ordering.extend(highest_priority_transitions)
        # 4. Remove the transitions of the highest-priority set from the graph, and repeat.
        remaining_edges = [(high,low) for high, low in remaining_edges if high not in highest_priority]
        remaining_transitions -= highest_priority_transitions

    # Finally, there may be transitions that occur in the priority graph only as vertices, e.g. in flat statecharts:
    concurrency.check_nondeterminism(tree, remaining_transitions, consistency)
    total_ordering.extend(remaining_transitions)

    return total_ordering

def priority_and_concurrency(statechart):
    graph = get_graph(statechart.tree, statechart.semantics)

    consistency = {
        Concurrency.SINGLE: concurrency.NoConcurrency(),
        Concurrency.MANY: concurrency.ArenaOrthogonal(),
    }[statechart.semantics.concurrency]

    priority_ordered_transitions = generate_total_ordering(statechart.tree, graph, consistency)

    return priority_ordered_transitions

