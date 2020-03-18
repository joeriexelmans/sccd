import lxml.etree as ET
import dataclasses
from copy import deepcopy

from sccd.syntax.statechart import *
from sccd.model.context import *
from sccd.model.parser import *
from sccd.model.xml_parser import *

# parent_node: XML node containing any number of action nodes as direct children
def load_actions(context: Context, datamodel, parent_node) -> List[Action]:
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
          block = parse_block(context, datamodel, block=action_node.text)
        except Exception as e:
          raise XmlLoadError(action_node, "Parsing code: %s" % str(e))
          # raise Exception("Line %d: <%s>: Error parsing code: '%s'" % (action_node.sourceline, tag, action_node.text))
        return Code(block)
      else:
        raise XmlLoadError(action_node, "Unsupported action tag.")
  return [load_action(child) for child in parent_node if child.tag is not ET.Comment]

# Load state tree from XML <tree> node.
# Context is required for building event namespace and in/outport discovery.
def load_tree(context: Context, datamodel, tree_node) -> StateTree:

  transition_nodes: List[Tuple[Any, State]] = [] # List of (<transition>, State) tuples

  # Recursively create state hierarchy from XML node
  # Adding <transition> elements to the 'transitions' list as a side effect
  def load_state(state_node, parent: State) -> Optional[State]:
    name = state_node.get("id", "")
    # tag = ET.QName(state_node).localname
    tag = state_node.tag
    if tag == "state":
        state = State(name, parent)
        initial = state_node.get("initial")
    elif tag == "parallel" : 
        state = ParallelState(name, parent)
    elif tag == "history":
      is_deep = state_node.get("type", "shallow") == "deep"
      if is_deep:
        state = DeepHistoryState(name, parent)
      else:
        state = ShallowHistoryState(name, parent)
    else:
      return None

    for xml_child in state_node.getchildren():
        if xml_child.tag is ET.Comment:
          continue # skip comments
        child = load_state(xml_child, parent=state) # may throw
        if child and tag == "state" and child.short_name == initial:
            state.default_state = child

    if tag == "state" and len(state.children) > 0 and not state.default_state:
      if len(state.children) == 1 and initial is None:
        state.default_state = state.children[0]

      if state.default_state is None:
        raise XmlLoadError(state_node, "Must set 'initial' attribute.")

    for xml_t in state_node.findall("transition", state_node.nsmap):
      transition_nodes.append((xml_t, state))

    # Parse enter/exit actions
    def _get_enter_exit(tag):
      node = state_node.find(tag, state_node.nsmap)
      if node is not None:
        return load_actions(context, datamodel, node)
      else:
        return []

    state.enter = _get_enter_exit("onentry")
    state.exit = _get_enter_exit("onexit")

    return state

  # Build tree structure
  root_node = tree_node.find("state")
  root = load_state(root_node, parent=None)

  # Add transitions
  next_after_id = 0
  for t_node, source in transition_nodes:
    try:
      # Parse and find target state
      target_string = t_node.get("target")
      parse_tree = parse_state_ref(target_string)
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
      raise XmlLoadError(t_node, "Could not find target '%s'" % target_string)

    transition = Transition(source, targets)

    # Trigger
    name = t_node.get("event")
    port = t_node.get("port")
    after = t_node.get("after")
    if after is not None:
      after_expr = parse_expression(context, datamodel, expr=after)
      # print(after_expr)
      name = "_after%d" % next_after_id # transition gets unique event name
      next_after_id += 1
      trigger = AfterTrigger(context.events.assign_id(name), name, after_expr)
    elif name is not None:
      trigger = Trigger(context.events.assign_id(name), name, port)
      context.inports.assign_id(port)
    else:
      trigger = None
    transition.trigger = trigger
    # Actions
    actions = load_actions(context, datamodel, t_node)
    transition.actions = actions
    # Guard
    cond = t_node.get("cond")
    if cond is not None:
      try:
        expr = parse_expression(context, datamodel, expr=cond)
        # print(expr)
      except Exception as e:
        raise XmlLoadError(t_node, "Condition '%s': %s" % (cond, str(e)))
      transition.guard = expr
    source.transitions.append(transition)

  return StateTree(root=root)

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
      val = parse_expression(context, datamodel, expr=expr)
      datamodel.create(id, val.eval([], datamodel))
      # datamodel.names[id] = Variable(val.eval([], datamodel))
  return datamodel

# Context is required for building event namespace and in/outport discovery.
def load_statechart(context: Context, sc_node) -> Statechart:
  datamodel_node = sc_node.find("datamodel")
  datamodel = load_datamodel(context, datamodel_node)

  tree_node = sc_node.find("tree")
  handler = TreeHandler(context, datamodel)
  parse(ET.iterwalk(tree_node, events=("start", "end")), handler)
  state_tree = handler.tree

  # tree_node = sc_node.find("tree")
  # state_tree = load_tree(context, datamodel, tree_node)

  semantics_node = sc_node.find("semantics")
  semantics = Semantics() # start with default semantics
  load_semantics(semantics, semantics_node)

  return Statechart(tree=state_tree, semantics=semantics, datamodel=datamodel)
