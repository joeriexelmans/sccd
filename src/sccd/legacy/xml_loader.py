# Legacy model and test loader

import os
import dataclasses
from typing import List, Any, Optional
import lxml.etree as ET
from lark import Lark

from sccd.syntax.statechart import *
from sccd.controller.controller import *
import sccd.schema

schema_dir = os.path.dirname(sccd.schema.__file__)

# Schema for XML validation
schema_path = os.path.join(schema_dir, "sccd.xsd")
schema = ET.XMLSchema(ET.parse(schema_path))

# Grammar for parsing state references and expressions
grammar = open(os.path.join(schema_dir,"grammar.g"))
parser = Lark(grammar, parser="lalr", start=["state_ref", "expr"])

@dataclass
class Test:
  input_events: List[InputEvent]
  expected_events: List[Event]

def load_model(src_file) -> Tuple[MultiInstanceModel, Optional[Test]]:
  tree = ET.parse(src_file)
  schema.assertValid(tree)
  root = tree.getroot()

  namespace = Namespace()
  model = MultiInstanceModel(namespace, classes={}, default_class=None)

  classes = root.findall(".//class", root.nsmap)
  for c in classes:
    class_name = c.get("name")
    default = c.get("default", "")

    scxml_node = c.find("scxml", root.nsmap)
    statechart = load_statechart(scxml_node, model.namespace)

    model.classes[class_name] = statechart
    if default or len(classes) == 1:
      model.default_class = class_name

  def find_ports(element_path, add_function):
    elements = root.findall(element_path, root.nsmap)
    for e in elements:
      port = e.get("port")
      if port != None:
        add_function(port)
  # Any 'port' attribute of a <transition> element is an input port
  find_ports(".//transition", namespace.add_inport)
  # Any 'port' attribute of a <raise> element is an output port
  find_ports(".//raise", namespace.add_outport)

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
        slot.append(Event(id=0, name=name, port=port, parameters=params))
      expected_events.append(slot)
    test = Test(input_events, expected_events)

  return (model, test)

def load_statechart(scxml_node, namespace: Namespace) -> Statechart:

  def load_action(action_node) -> Optional[Action]:
    tag = ET.QName(action_node).localname
    if tag == "raise":
      event = action_node.get("event")
      port = action_node.get("port")
      if not port:
        return RaiseInternalEvent(name=event, parameters=[], event_id=namespace.assign_event_id(event))
      else:
        return RaiseOutputEvent(name=event, parameters=[], outport=port, time_offset=0)
    else:
      raise None

  # parent_node: XML node containing any number of action nodes as direct children
  def load_actions(parent_node) -> List[Action]:
    return list(filter(lambda x: x is not None, map(lambda child: load_action(child), parent_node)))

  transitions: List[Tuple[Any, State]] = [] # List of (<transition>, State) tuples

  # Recursively create state hierarchy from XML node
  # Adding <transition> elements to the 'transitions' list as a side effect
  def build_tree(xml_node) -> Optional[State]:
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
      return None

    initial = xml_node.get("initial", "")
    for xml_child in xml_node.getchildren():
        child = build_tree(xml_child) # may throw
        if child:
          state.addChild(child)
          if child.short_name == initial:
            state.default_state = child
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

  # Get tree from XML
  root = build_tree(scxml_node)

  # Add transitions
  next_after_id = 0
  for xml_t, source in transitions:
    # Parse and find target state
    target_string = xml_t.get("target", "")
    parse_tree = parser.parse(target_string, start="state_ref")
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
    after = xml_t.get("after")
    if after is not None:
      event = "_after%d" % next_after_id # transition gets unique event name
      next_after_id += 1
      trigger = AfterTrigger(namespace.assign_event_id(event), event, IntLiteral(int(after)))
    elif event is not None:
      trigger = Trigger(namespace.assign_event_id(event), event, port)
    else:
      trigger = None
    transition.setTrigger(trigger)
    # Actions
    actions = load_actions(xml_t)
    transition.setActions(actions)
    # Guard
    cond = xml_t.get("cond")
    if cond is not None:
      parse_tree = parser.parse(cond, start="expr")
      # print(parse_tree)
      # print(parse_tree.pretty())
      cond_expr = load_expression(parse_tree)
      transition.setGuard(cond_expr)
    source.addTransition(transition)

  # Calculate stuff like list of ancestors, descendants, etc.
  # Also get depth-first ordered lists of states and transitions (by source)
  states: Dict[str, State] = {}
  state_list: List[State] = []
  transition_list: List[Transition] = []
  root.init_tree(0, "", states, state_list, transition_list)

  for t in transition_list:
    t.optimize()

  # Semantics - We use reflection to find the xml attribute names and values
  semantics = Semantics()
  for aspect in dataclasses.fields(Semantics):
    key = scxml_node.get(aspect.name)
    if key is not None:
      value = aspect.type[key.upper()]
      setattr(semantics, aspect.name, value)

  return Statechart(
    tree=StateTree(root=root, states=states, state_list=state_list, transition_list=transition_list),
    datamodel=DataModel(),
    semantics=semantics)

class ParseError(Exception):
  def __init__(self, msg):
    self.msg = msg

def load_expression(parse_node) -> Expression:
  if parse_node.data == "func_call":
    function = load_expression(parse_node.children[0])
    parameters = [load_expression(e) for e in parse_node.children[1].children]
    return FunctionCall(function, parameters)
  elif parse_node.data == "string":
    return StringLiteral(parse_node.children[0].value[1:-1])
  elif parse_node.data == "identifier":
    return Identifier(parse_node.children[0].value)
  elif parse_node.data == "array":
    elements = [load_expression(e) for e in parse_node.children]
    return Array(elements)
  raise ParseError("Can't handle expression type: "+parse_node.data)
