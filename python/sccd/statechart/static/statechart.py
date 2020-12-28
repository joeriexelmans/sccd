from sccd.statechart.static.tree import *
from sccd.action_lang.static.scope import *
from sccd.statechart.static.semantic_configuration import *

@dataclass(eq=False)
class Statechart(Visitable):
    # __slots__ = ["semantics", "scope", "datamodel", "in_events", "out_events", "internal_events", "tree"]

    # Semantic configuration for statechart execution
    semantics: SemanticConfiguration = field(default_factory=SemanticConfiguration)

    # Instance scope, the set of variable names (and their types and offsets in memory) that belong to the statechart
    scope: Scope = None # for datamodel

    # Block of statements setting up the datamodel (variables in instance scope)
    datamodel: Optional[Block] = None

    # Mapping from event name to event parameter types
    in_events: Dict[str, List[SCCDType]] = field(default_factory=dict)
    
    # Mapping from event name to event parameter types
    out_events: Dict[str, List[SCCDType]] = field(default_factory=dict)
    
    # Mapping from event name to event parameter types
    internal_events: Dict[str, List[SCCDType]] = field(default_factory=dict)

    tree: StateTree = None


    def generate_semantic_variants(self) -> List['Statechart']:
        return [
            Statechart(
                semantics=variant,
                #  All other fields remain the same.
                scope=self.scope,
                datamodel=self.datamodel,
                in_events=self.in_events,
                out_events=self.out_events,
                internal_events=self.internal_events,
                tree=self.tree)
            for variant in self.semantics.generate_variants()]
