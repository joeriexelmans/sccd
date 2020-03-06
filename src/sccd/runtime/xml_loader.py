import os
import dataclasses
from typing import List, Any, Optional
import lxml.etree as ET
from lark import Lark
import sccd.compiler
from sccd.runtime.statechart_syntax import *
from sccd.runtime.event import Event
from sccd.runtime.semantic_options import SemanticConfiguration

schema_path = os.path.join(
  os.path.dirname(sccd.compiler.__file__),
  "schema",
  "sccd.xsd")
schema = ET.XMLSchema(ET.parse(schema_path))

grammar = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"grammar.g"))
l = Lark(grammar, parser="lalr", start=["target_expr"])


# Some types immitating the types that are produced by the compiler
@dataclass
class Statechart:
  _class: Any
  root: State
  states: Dict[str, State]
  semantics: SemanticConfiguration

@dataclass
class Class:
  name: str
  statechart: Statechart

@dataclass
class Model:
  inports: List[str]
  outports: List[str]
  classes: Dict[str, Any]
  default_class: str

@dataclass
class InputEvent:
  name: str
  port: str
  parameters: List[Any]
  time_offset: Timestamp

@dataclass
class Test:
  input_events: List[InputEvent]
  expected_events: List[Event]


def load_model(src_file) -> Tuple[Model, Optional[Test]]:
  tree = ET.parse(src_file)
  schema.assertValid(tree)
  root = tree.getroot()

  model = Model([], [], {}, "")

  classes = root.findall(".//class", root.nsmap)
  for c in classes:
    class_name = c.get("name")
    default = c.get("default", "")

    scxml_node = c.find("scxml", root.nsmap)
    root_state, states = load_tree(scxml_node)

    # Semantics - We use reflection to find the xml attribute names and values
    semantics = SemanticConfiguration()
    for aspect in dataclasses.fields(SemanticConfiguration):
      key = scxml_node.get(aspect.name)
      if key is not None:
        value = aspect.type[key.upper()]
        setattr(semantics, aspect.name, value)

    class_ = Class(class_name, None)
    statechart = Statechart(class_, root_state, states, semantics)
    class_.statechart = statechart

    model.classes[class_name] = lambda: class_
    if default:
      model.default_class = class_name

  def find_ports(element_path, collection):
    elements = root.findall(element_path, root.nsmap)
    for e in elements:
      port = e.get("port")
      if port != None and port not in collection:
        collection.append(port)
  # Any 'port' attribute of a <transition> element is an input port
  find_ports(".//transition", model.inports)
  # Any 'port' attribute of a <raise> element is an output port
  find_ports(".//raise", model.outports)

  test = None
  test_node = root.find(".//test", root.nsmap)
  if test_node is not None:
    input_events = []
    expected_events = []
    input_node = test_node.find("input", root.nsmap)
    if input_node is not None:
      for event_node in input_node:
        name = event_node.get("name")
        port = event_node.get("port")
        time = int(event_node.get("time"))
        input_events.append(InputEvent(name, port, [], time))
    slots = test_node.findall("expected/slot", root.nsmap)
    for s in slots:
      slot = []
      events = s.findall("event", root.nsmap)
      for e in events:
        name = e.get("name")
        port = e.get("port")
        params = [] # todo: read params
        slot.append(Event(name, port, params))
      expected_events.append(slot)
    test = Test(input_events, expected_events)

  return (model, test)

class InvalidTag(Exception):
  pass

def load_tree(scxml_node) -> Tuple[State, Dict[str, State]]:

  states: Dict[str, State] = {}
  transitions: List[Tuple[Any, State]] = [] # List of (<transition>, State) tuples


  # Recursively create state hierarchy from XML node
  # Adding <transition> elements to the 'transitions' list as a side effect
  def _get_state_tree(xml_node) -> State:
    state = None
    name = xml_node.get("id", "")
    tag = ET.QName(xml_node).localname
    if tag == "scxml" or tag == "state":
        state = State(name)
    elif tag == "parallel" : 
        state = ParallelState(name)
    elif tag == "history":
      is_deep = xml_node.get("type", "shallow") == "deep"
      if is_deep:
        state = DeepHistoryState(name)
      else:
        state = ShallowHistoryState(name)
    else:
      raise InvalidTag()

    initial = xml_node.get("initial", "")
    for xml_child in xml_node.getchildren():
      try:
        child = _get_state_tree(xml_child) # may throw
        state.addChild(child)
        if child.short_name == initial:
          state.default_state = child
      except InvalidTag:
        pass # skip non-state tags

    if not initial and len(state.children) == 1:
        state.default_state = state.children[0]

    for xml_t in xml_node.findall("transition", xml_node.nsmap):
      transitions.append((xml_t, state))

    # Parse enter/exit actions
    def _get_enter_exit(tag, setter):
      node = xml_node.find(tag, xml_node.nsmap)
      if node is not None:
        actions = load_actions(node)
        setter(actions)

    _get_enter_exit("onentry", state.setEnter)
    _get_enter_exit("onexit", state.setExit)

    return state

  # First build a state tree
  root = _get_state_tree(scxml_node)
  root.init_tree(0, "", states)

  # Add transitions
  for xml_t, source in transitions:
    # Parse and find target state
    target_string = xml_t.get("target", "")
    parse_tree = l.parse(target_string, start="target_expr")
    def find_state(sequence) -> State:
      if sequence.data == "relative_path":
        el = source
      elif sequence.data == "absolute_path":
        el = root
      for item in sequence.children:
        if item.type == "PARENT_NODE":
          el = el.parent
        elif item.type == "CURRENT_NODE":
          continue
        elif item.type == "IDENTIFIER":
          el = [x for x in el.children if x.short_name == item.value][0]
      return el
    targets = [find_state(seq) for seq in parse_tree.children]

    transition = Transition(source, targets)

    # Trigger
    event = xml_t.get("event")
    port = xml_t.get("port")
    trigger = None if event == None else Trigger(event, port)
    transition.setTrigger(trigger)
    # Actions
    actions = load_actions(xml_t)
    transition.setActions(actions)
    # todo: set guard

    source.addTransition(transition)

  return (root, states)

def load_action(action_node) -> Optional[Action]:
  tag = ET.QName(action_node).localname
  if tag == "raise":
    event = action_node.get("event")
    port = action_node.get("port")
    if not port:
      return RaiseInternalEvent(name=event, parameters=[])
    else:
      return RaiseOutputEvent(name=event, parameters=[], outport=port, time_offset=0)
  else:
    raise InvalidTag()

# parent_node: XML node containing 0 or more action nodes as direct children
def load_actions(parent_node) -> List[Action]:
  actions = []
  for node in parent_node:
    try:
      a = load_action(node)
      if a:
        actions.append(a)
    except InvalidTag:
      pass # skip non-action tags
  return actions