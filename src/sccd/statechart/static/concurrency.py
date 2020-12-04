from sccd.common.exceptions import *
from sccd.statechart.static.tree import *
from abc import *

class SmallStepConsistency:
    @abstractmethod
    def can_fire_together(self, t1: Transition, t2: Transition) -> bool:
        pass

class NoConcurrency(SmallStepConsistency):
    def can_fire_together(self, t1: Transition, t2: Transition) -> bool:
        return False

class ArenaOrthogonal(SmallStepConsistency):
    def can_fire_together(self, t1: Transition, t2: Transition) -> bool:
        return not (t1.arena_bitmap & t2.arena_bitmap) # nonoverlapping arenas

class SrcDstOrthogonal(SmallStepConsistency):
    def __init__(self, tree: StateTree):
        self.tree = tree

    def can_fire_together(self, t1: Transition, t2: Transition) -> bool:
        source_lca = self.tree.lca(t1.source, t2.source)
        target_lca = self.tree.lca(t1.target, t2.target)
        return isinstance(source_lca.type, AndState) and isinstance(target_lca.type, AndState)

# Raises an exception if the given set of transitions can potentially be enabled simulatenously, wrt. their source states in the state tree.
def check_nondeterminism(tree: StateTree, transitions: Iterable[Transition], consistency: SmallStepConsistency):
    pairs = itertools.combinations(transitions, 2)
    for t1, t2 in pairs:
        if consistency.can_fire_together(t1, t2):
            return # It's OK: if they are both enabled, they will fire together in a small step

        # They have the same source:
        if t1.source is t2.source:
            raise ModelStaticError("Nondeterminism! No priority between outgoing transitions of same state: %s, %s" % (t1, t2))
        # Their sources are orthogonal to each other:
        lca = tree.lca(t1.source, t2.source)
        if isinstance(lca.type, AndState):
            raise ModelStaticError("Nondeterminism! No priority between orthogonal transitions: %s, %s" % (t1, t2))
        # Their source states are ancestors of one another:
        if is_ancestor(t1.source, t2.source) or is_ancestor(t2.source, t1.source):
            raise ModelStaticError("Nondeterminism! No priority between ancestral transitions: %s, %s" % (t1, t2))
