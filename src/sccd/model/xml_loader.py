import os
import lxml.etree as ET
import dataclasses
from copy import deepcopy
from lark import Lark, Transformer

from sccd.syntax.statechart import *
from sccd.model.context import *

import sccd.schema

with open(os.path.join(os.path.dirname(sccd.schema.__file__),"grammar.g")) as file:
  _grammar = file.read()

# Lark transformer for parsetree-less parsing of expressions
class _ExpressionTransformer(Transformer):
  def __init__(self):
    super().__init__()
    self.context: Context = None
  array = Array
  block = Block
  def string(self, node):
    return StringLiteral(node[0][1:-1])
  def int(self, node):
    return IntLiteral(int(node[0].value))
  def func_call(self, node):
    return FunctionCall(node[0], node[1].children)
  def identifier(self, node):
    return Identifier(node[0].value)
  def binary_expr(self, node):
    return BinaryExpression(node[0], node[1].value, node[2])
  def unary_expr(self, node):
    return UnaryExpression(node[0].value, node[1])
  def bool(self, node):
    return BoolLiteral({
      "True": True,
      "False": False,
      }[node[0].value])
  def group(self, node):
    return Group(node[0])
  def assignment(self, node):
    return Assignment(node[0], node[1].value, node[2])
  def duration(self, node):
    unit = {
      "fs": FemtoSecond,
      "ps": PicoSecond,
      "ns": Nanosecond,
      "us": Microsecond,
      "ms": Millisecond,
      "s": Second,
      "m": Minute,
      "h": Hour
    }[node[0].children[1]]
    d = DurationLiteral(Duration(int(node[0].children[0]),unit))
    self.context.durations.append(d)
    return d

# Global variables so we don't have to rebuild our parser every time
_transformer = _ExpressionTransformer()
_expr_parser = Lark(_grammar, parser="lalr", start=["expr", "block"], transformer=_transformer)
_state_ref_parser = Lark(_grammar, parser="lalr", start=["state_ref"])

def parse_expression(context: Context, expr: str) -> Expression:
  _transformer.context = context
  return _expr_parser.parse(expr, start="expr")

def parse_block(context: Context, block: str) -> Statement:
  _transformer.context = context
  return _expr_parser.parse(block, start="block")

# parent_node: XML node containing any number of action nodes as direct children
def load_actions(context: Context, parent_node) -> List[Action]:
  def load_action(action_node) -> Optional[Action]:
      # tag = ET.QName(action_node).localname
      tag = action_node.tag
      if tag == "raise":
        name = action_node.get("event")
        port = action_node.get("port")
        if not port:
          event_id = context.events.assign_id(name)
          return RaiseInternalEvent(name=name, parameters=[], event_id=event_id)
        else:
          context.outports.assign_id(port)
          return RaiseOutputEvent(name=name, parameters=[], outport=port, time_offset=0)
      elif tag == "code":
        try:
          block = parse_block(context, block=action_node.text)
        except:
          raise Exception("Line %d: <%s>: Error parsing code: '%s'" % (action_node.sourceline, tag, action_node.text))
        return Code(block)
      else:
        raise Exception("Line %d: <%s>: Unsupported action tag." % (action_node.sourceline, tag))
  return [load_action(child) for child in parent_node if child.tag is not ET.Comment]

# Load state tree from XML <tree> node.
# Context is required for building event namespace and in/outport discovery.
def load_tree(context: Context, tree_node) -> StateTree:

  transition_nodes: List[Tuple[Any, State]] = [] # List of (<transition>, State) tuples

  # Recursively create state hierarchy from XML node
  # Adding <transition> elements to the 'transitions' list as a side effect
  def load_state(state_node) -> Optional[State]:
    state = None
    name = state_node.get("id", "")
    # tag = ET.QName(state_node).localname
    tag = state_node.tag
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
        if xml_child.tag is ET.Comment:
          continue # skip comments
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
        actions = load_actions(context, node)
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
      parse_tree = _state_ref_parser.parse(target_string, start="state_ref")
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
      after_expr = parse_expression(context, expr=after)
      # print(after_expr)
      name = "_after%d" % next_after_id # transition gets unique event name
      next_after_id += 1
      trigger = AfterTrigger(context.events.assign_id(name), name, after_expr)
    elif name is not None:
      trigger = Trigger(context.events.assign_id(name), name, port)
      context.inports.assign_id(port)
    else:
      trigger = None
    transition.setTrigger(trigger)
    # Actions
    actions = load_actions(context, t_node)
    transition.setActions(actions)
    # Guard
    cond = t_node.get("cond")
    if cond is not None:
      try:
        # _expr_parser2 = Lark(grammar, parser="lalr", start=["expr"])
        # tree2 = _expr_parser2.parse(cond, start="expr")
        # print(tree2.pretty())

        expr = _expr_parser.parse(cond, start="expr")
        # print(expr)
        transition.setGuard(expr)
      except Exception as e:
        raise Exception("Line %d: <transition> with cond=\"%s\": %s" % (t_node.sourceline, cond, str(e)))
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

def load_semantics(semantics: Semantics, semantics_node):
  if semantics_node is not None:
    # Use reflection to find the possible XML attributes and their values
    for aspect in dataclasses.fields(Semantics):
      key = semantics_node.get(aspect.name)
      if key is not None:
        if key == "*":
          setattr(semantics, aspect.name, None)
        else:
          value = aspect.type[key.upper()]
          setattr(semantics, aspect.name, value)

def load_datamodel(context: Context, datamodel_node) -> DataModel:
  datamodel = DataModel()
  if datamodel_node is not None:
    for var_node in datamodel_node.findall("var"):
      id = var_node.get("id")
      expr = var_node.get("expr")
      val = parse_expression(context, expr=expr)
      datamodel.names[id] = Variable(val.eval([], datamodel))
  return datamodel

# Context is required for building event namespace and in/outport discovery.
def load_statechart(context: Context, sc_node) -> Statechart:
  datamodel_node = sc_node.find("datamodel")
  datamodel = load_datamodel(context, datamodel_node)

  tree_node = sc_node.find("tree")
  state_tree = load_tree(context, tree_node)

  semantics_node = sc_node.find("semantics")
  semantics = Semantics() # start with default semantics
  load_semantics(semantics, semantics_node)

  return Statechart(tree=state_tree, semantics=semantics, datamodel=datamodel)
