import os
import dataclasses
from typing import List, Any, Optional
import lxml.etree as ET
from lark import Lark
import sccd.compiler
from sccd.runtime.statechart_syntax import *
from sccd.runtime.event import Event
from sccd.runtime.semantic_options import *

schema_path = os.path.join(
  os.path.dirname(sccd.compiler.__file__),
  "schema",
  "sccd.xsd")
schema = ET.XMLSchema(ET.parse(schema_path))

grammar = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"grammar.g"))
l = Lark(grammar)

@dataclass
class Statechart:
  _class: Any
  root: State
  states: Dict[str, State]
  semantics: SemanticOptions

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
class Test:
  input_events: List[Any]
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
    semantics = SemanticOptions()
    for aspect in dataclasses.fields(SemanticOptions):
      key = scxml_node.get(aspect.name)
      if key is not None:
        value = aspect.type[key.upper()]
        setattr(semantics, aspect.name, value)
    print(semantics)
    class_ = Class(class_name, None)
    statechart = Statechart(class_, root_state, states, semantics)
    class_.statechart = statechart
    model.classes[class_name] = lambda: class_
    if default:
      model.default_class = class_name

  transitions = root.findall(".//transition", root.nsmap)
  for t in transitions:
    port = t.get("port", "")
    if port != "" and port not in model.outports:
      print("found port", port)
      model.outports.append(port)

  test = None
  test_node = root.find(".//test", root.nsmap)
  if test_node is not None:
    input_events = []
    expected_events = []
    input_node = test_node.find("input", root.nsmap)
    if input_node:
      pass
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


def load_tree(scxml_node) -> Tuple[State, Dict[str, State]]:

  states: Dict[str, State] = {}
  transitions: List[Tuple[Any, State]] = [] # List of (<transition>, State) tuples

  class InvalidTag(Exception):
    pass

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
        pass

    if not initial and len(state.children) == 1:
        state.default_state = state.children[0]

    for xml_t in xml_node.findall("transition", xml_node.nsmap):
      transitions.append((xml_t, state))
    return state

  # First build a state tree
  root = _get_state_tree(scxml_node)
  root.init_tree(0, "", states)

  # Add transitions
  for xml_t, source in transitions:
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
    # todo: set guard
    # todo: set trigger
    transition.setTrigger(None)
    # todo: set actions
    source.addTransition(transition)

  return (root, states)
