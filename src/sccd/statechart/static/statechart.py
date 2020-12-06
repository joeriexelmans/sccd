from sccd.statechart.static.tree import *
from sccd.action_lang.static.scope import *
from sccd.statechart.static.semantic_configuration import *

@dataclass
class Statechart(Freezable, Visitable):
  __slots__ = ["semantics", "scope", "datamodel", "internal_events", "internally_raised_events", "inport_events", "event_outport", "tree"]

  def __init__(self, semantics: SemanticConfiguration, scope: Scope, datamodel: Optional[Block], internal_events: Bitmap, internally_raised_events: Bitmap, inport_events: Dict[str, Set[int]], event_outport: Dict[str, str], tree: StateTree):
    
    super().__init__()
  
    # Semantic configuration for statechart execution
    self.semantics: SemanticConfiguration = semantics

    # Instance scope, the set of variable names (and their types and offsets in memory) that belong to the statechart
    self.scope: Scope = scope

    # Block of statements setting up the datamodel (variables in instance scope)
    self.datamodel: Optional[Block] = datamodel

    # Union of internally raised and input events. Basically all the events that a transition could be triggered by.
    self.internal_events: Bitmap = internal_events
    
    # All internally raised events in the statechart, may overlap with input events, as an event can be both an input event and internally raised.
    self.internally_raised_events: Bitmap = internally_raised_events

    # Mapping from inport to set of event IDs - currently unused
    self.inport_events: Dict[str, Bitmap] = inport_events
    # Mapping from event name to outport
    self.event_outport: Dict[str, str] = event_outport

    self.tree: StateTree = tree

  def generate_semantic_variants(self) -> List['Statechart']:
    return [Statechart(
        semantics=variant,
        #  All other fields remain the same.
        scope=self.scope,
        datamodel=self.datamodel,
        internal_events=self.internal_events,
        internally_raised_events=self.internally_raised_events,
        inport_events=self.inport_events,
        event_outport=self.event_outport,
        tree=self.tree)
      for variant in self.semantics.generate_variants()]
