import os
import lxml.etree as ET
from lark import Lark, Transformer
from sccd.runtime.test import *
from sccd.runtime.model import *
from sccd.runtime.statechart_syntax import *

import sccd.schema
schema_dir = os.path.dirname(sccd.schema.__file__)

with open(os.path.join(schema_dir,"grammar.g")) as file:
  grammar = file.read()

# Lark transformer for parsetree-less parsing of expressions
class ExpressionTransformer(Transformer):
  def string(self, node):
    return StringLiteral(node[0][1:-1])

  def func_call(self, node):
    return FunctionCall(node[0], node[1].children)

  def identifier(self, node):
    return Identifier(node[0].value)

  array = Array

expr_parser = Lark(grammar, parser="lalr", start=["expr"], transformer=ExpressionTransformer())

state_ref_parser = Lark(grammar, parser="lalr", start=["state_ref"])

# Load state tree from XML <tree> node.
# Namespace is required for building event namespace and in/outport discovery.
def load_state_tree(namespace: ModelNamespace, tree_node) -> StateTree:
  def load_action(action_node) -> Optional[Action]:
    tag = ET.QName(action_node).localname
    if tag == "raise":
      name = action_node.get("event")
      port = action_node.get("port")
      if not port:
        event_id = namespace.assign_event_id(name)
        return RaiseInternalEvent(name=name, parameters=[], event_id=event_id)
      else:
        namespace.add_outport(port)
        return RaiseOutputEvent(name=name, parameters=[], outport=port, time_offset=0)
    else:
      raise Exception("Unsupported action")

  # parent_node: XML node containing any number of action nodes as direct children
  def load_actions(parent_node) -> List[Action]:
    return list(filter(lambda x: x is not None, map(lambda child: load_action(child), parent_node)))

  transition_nodes: List[Tuple[Any, State]] = [] # List of (<transition>, State) tuples

  # Recursively create state hierarchy from XML node
  # Adding <transition> elements to the 'transitions' list as a side effect
  def load_state(state_node) -> Optional[State]:
    state = None
    name = state_node.get("id", "")
    tag = ET.QName(state_node).localname
    if tag == "state":
        state = State(name)
    elif tag == "parallel" : 
        state = ParallelState(name)
    elif tag == "history":
      is_deep = state_node.get("type", "shallow") == "deep"
      if is_deep:
        state = DeepHistoryState(name)
      else:
        state = ShallowHistoryState(name)
    else:
      return None

    initial = state_node.get("initial", "")
    for xml_child in state_node.getchildren():
        child = load_state(xml_child) # may throw
        if child:
          state.addChild(child)
          if child.short_name == initial:
            state.default_state = child
    if tag == "state" and not initial:
      if len(state.children) == 1:
        state.default_state = state.children[0]
      elif len(state.children) > 1:
        raise Exception("Line %d: <%s> with %d children: Must set 'initial' attribute." % (state_node.sourceline, tag, len(state.children)))

    for xml_t in state_node.findall("transition", state_node.nsmap):
      transition_nodes.append((xml_t, state))

    # Parse enter/exit actions
    def _get_enter_exit(tag, setter):
      node = state_node.find(tag, state_node.nsmap)
      if node is not None:
        actions = load_actions(node)
        setter(actions)

    _get_enter_exit("onentry", state.setEnter)
    _get_enter_exit("onexit", state.setExit)

    return state

  # Build tree structure
  root_node = tree_node.find("state")
  root = load_state(root_node)

  # Add transitions
  next_after_id = 0
  for t_node, source in transition_nodes:
    try:
      # Parse and find target state
      target_string = t_node.get("target", "")
      parse_tree = state_ref_parser.parse(target_string, start="state_ref")
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
    except:
      raise Exception("Line %d: <transition> with target=\"%s\": Could not find target." % (t_node.sourceline, target_string))

    transition = Transition(source, targets)

    # Trigger
    name = t_node.get("event")
    port = t_node.get("port")
    after = t_node.get("after")
    if after is not None:
      name = "_after%d" % next_after_id # transition gets unique event name
      next_after_id += 1
      trigger = AfterTrigger(namespace.assign_event_id(name), name, Timestamp(after))
    elif name is not None:
      trigger = Trigger(namespace.assign_event_id(name), name, port)
      namespace.add_inport(port)
    else:
      trigger = None
    transition.setTrigger(trigger)
    # Actions
    actions = load_actions(t_node)
    transition.setActions(actions)
    # Guard
    cond = t_node.get("cond")
    if cond is not None:
      expr = expr_parser.parse(cond, start="expr")
      transition.setGuard(expr)
    source.addTransition(transition)

  # Calculate stuff like list of ancestors, descendants, etc.
  # Also get depth-first ordered lists of states and transitions (by source)
  states: Dict[str, State] = {}
  state_list: List[State] = []
  transition_list: List[Transition] = []
  root.init_tree(0, "", states, state_list, transition_list)

  for t in transition_list:
    t.optimize()

  return StateTree(root=root, states=states, state_list=state_list, transition_list=transition_list)

# Namespace is required for building event namespace and in/outport discovery.
def load_statechart(namespace: ModelNamespace, sc_node) -> Statechart:
  tree_node = sc_node.find("tree")
  state_tree = load_state_tree(namespace, tree_node)

  semantics_node = sc_node.find("semantics")
  semantics = SemanticConfiguration() # start with default semantics
  load_semantics(semantics, semantics_node)

  datamodel_node = sc_node.find("datamodel")
  # TODO: process datamodel node

  return Statechart(tree=state_tree, semantics=semantics)

def load_semantics(semantics: SemanticConfiguration, semantics_node):
    if semantics_node is not None:
      # Use reflection to find the possible XML attributes and their values
      for aspect in dataclasses.fields(SemanticConfiguration):
        key = semantics_node.get(aspect.name)
        if key is not None:
          if key == "*":
            setattr(semantics, aspect.name, None)
          else:
            value = aspect.type[key.upper()]
            setattr(semantics, aspect.name, value)

# Returned list contains more than one test if the semantic configuration contains wildcard values.
def load_test(src_file) -> List[Test]:
  namespace = ModelNamespace()

  test_node = ET.parse(src_file).getroot()
  sc_node = test_node.find("statechart")
  src = sc_node.get("src")
  if src is None:
    statechart = load_statechart(namespace, sc_node)
  else:
    external_node = ET.parse(os.path.join(os.path.dirname(src_file), src)).getroot()
    statechart = load_statechart(namespace, external_node)
    semantics_node = sc_node.find("override_semantics")
    load_semantics(statechart.semantics, semantics_node)

  input_node = test_node.find("input")
  output_node = test_node.find("output")
  input = load_input(input_node)
  output = load_output(output_node)

  def variant_description(i, variant) -> str:
    if not variant:
      return ""
    return " (variant %d: %s)" % (i, ",".join(str(val) for val in variant.values()))

  return [
    Test(
      src_file + variant_description(i, variant),
      SingleInstanceModel(
        namespace,
        Statechart(tree=statechart.tree, semantics=dataclasses.replace(statechart.semantics, **variant))),
      input,
      output)
    for i, variant in enumerate(statechart.semantics.wildcard_cart_product())
  ]

def load_input(input_node) -> TestInput:
  input = []
  if input_node is not None:
    for event_node in input_node:
      name = event_node.get("name")
      port = event_node.get("port")
      time = int(event_node.get("time"))
      input.append(InputEvent(name, port, [], time))
  return input

def load_output(output_node) -> TestOutput:
  output = []
  if output_node is not None: 
    for big_step_node in output_node:
      big_step = []
      for event_node in big_step_node:
        name = event_node.get("name")
        port = event_node.get("port")
        parameters = [] # todo: read params
        big_step.append(Event(id=0, name=name, port=port, parameters=parameters))
      output.append(big_step)
  return output
