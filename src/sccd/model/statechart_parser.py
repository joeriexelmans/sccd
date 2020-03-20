import dataclasses
from lxml import etree
from sccd.model.expression_parser import *
from sccd.syntax.statechart import *
from sccd.syntax.tree import *


class XmlLoadError(Exception):
  def __init__(self, src_file: str, el: etree.Element, err):
    parent = el.getparent()
    if parent is None:
      parent = el
    # el = parent
    lines = etree.tostring(parent).decode('utf-8').strip().split('\n')
    nbr_lines = len(etree.tostring(el).decode('utf-8').strip().split('\n'))
    lines_numbers = []
    l = parent.sourceline
    for line in lines:
      ll = ("%4d: " % l) + line
      if l >= el.sourceline and l < el.sourceline + nbr_lines:
        ll = termcolor.colored(ll, 'yellow')
      lines_numbers.append(ll)
      l += 1
    super().__init__("\n\n%s\n\n%s:\nline %d: <%s>: %s" % ('\n'.join(lines_numbers), src_file,el.sourceline, el.tag, str(err)))


class Parser:

  def __init__(self):
    self.stacks: Dict[str, List[Any]] = {}

  def _init_stack(self, name):
    return self.stacks.setdefault(name, [])

  def push(self, name, value):
    stack = self._init_stack(name)
    stack.append(value)

  def pop(self, name):
    return self.stacks[name].pop()

  def get(self, name, default=None):
    stack = self._init_stack(name)
    return stack[-1] if len(stack) else default

  def require(self, name):
    try:
      return self.stacks[name][-1]
    except:
      raise Exception("Element expected only within context: %s" % name)

  def all(self, name):
    stack = self._init_stack(name)
    return stack

  def parse(self, src_file):
    self.push("src_file", src_file)

    for event, el in etree.iterparse(src_file, events=("start", "end")):
      # print(event, el.tag)
      try:
        if event == "start":
          start_method = getattr(self, "start_"+el.tag, None)
          if start_method:
            start_method(el)

        elif event == "end":
          end_method = getattr(self, "end_"+el.tag)
          if end_method:
            end_method(el)

      except XmlLoadError:
        raise
      # Decorate non-XmlLoadErrors
      except Exception as e:
        self._raise(el, e)

      # We don't need anything from this element anymore, so we clear it to save memory.
      # This is a technique mentioned in the lxml documentation:
      # https://lxml.de/tutorial.html#event-driven-parsing
      # el.clear()
      
    self.pop("src_file")

  def _raise(self, el, err):
    src_file = self.require("src_file")
    raise XmlLoadError(src_file, el, err)

class StatechartParser(Parser):

  def end_var(self, el):
    context = self.require("context")
    datamodel = self.require("datamodel")

    id = el.get("id")
    expr = el.get("expr")
    parsed = parse_expression(context, datamodel, expr=expr)
    datamodel.create(id, parsed.eval([], datamodel))

  def start_datamodel(self, el):
    statechart = self.require("statechart")
    self.push("datamodel", statechart.datamodel)

  def end_datamodel(self, el):
    self.pop("datamodel")


  def end_raise(self, el):
    context = self.require("context")
    actions = self.require("actions")
    name = el.get("event")
    port = el.get("port")
    if not port:
      event_id = context.events.assign_id(name)
      a = RaiseInternalEvent(name=name, parameters=[], event_id=event_id)
    else:
      context.outports.assign_id(port)
      a = RaiseOutputEvent(name=name, parameters=[], outport=port, time_offset=0)
    actions.append(a)

  def end_code(self, el):
    context = self.require("context")
    datamodel = self.require("datamodel")
    actions = self.require("actions")

    block = parse_block(context, datamodel, block=el.text)
    a = Code(block)
    actions.append(a)


  def _internal_start_state(self, el, constructor):
    parent = self.get("state", default=None)

    short_name = el.get("id", "")
    if parent is None:
      if short_name:
        raise Exception("Root <state> must not have 'id' attribute.")
    else:
      if not short_name:
        raise Exception("Non-root <state> must have 'id' attribute.")

    state = constructor(short_name, parent)

    parent_children = self.require("state_children")
    already_there = parent_children.setdefault(short_name, state)
    if already_there is not state:
      if parent:
        raise Exception("Sibling state with the same id exists.")
      else:
        raise Exception("Only 1 root <state> allowed.")

    self.push("state", state)
    self.push("state_children", {})

  def _internal_end_state(self):
    state_children = self.pop("state_children")
    state = self.pop("state")
    return (state, state_children)


  def start_state(self, el):
    self._internal_start_state(el, State)

  def end_state(self, el):
    state, state_children = self._internal_end_state()

    initial = el.get("initial", None)
    if initial is not None:
      state.default_state = state_children[initial]
    elif len(state.children) == 1:
      state.default_state = state.children[0]
    elif len(state.children) > 1:
      raise Exception("More than 1 child state: must set 'initial' attribute.")

  def start_parallel(self, el):
    self._internal_start_state(el, ParallelState)

  def end_parallel(self, el):
    self._internal_end_state()

  def start_history(self, el):
    if el.get("type", "shallow") == "deep":
      self._internal_start_state(el, DeepHistoryState)
    else:
      self._internal_start_state(el, ShallowHistoryState)

  def end_history(self, el):
    return self._internal_end_state()


  def start_onentry(self, el):
    self.push("actions", [])

  def end_onentry(self, el):
    actions = self.pop("actions")
    self.require("state").enter = actions

  def start_onexit(self, el):
    self.push("actions", [])

  def end_onexit(self, el):
    actions = self.pop("actions")
    self.require("state").exit = actions


  def start_transition(self, el):
    self.push("actions", [])

  def end_transition(self, el):
    actions = self.pop("actions")
    # simply accumulate transition elements
    # we'll deal with them in end_tree()
    source = self.require("state")

    # get stuff from element
    target = el.get("target", "")
    event = el.get("event")
    port = el.get("port")
    after = el.get("after")
    cond = el.get("cond")

    self.require("transitions").append((el, target, event, port, after, cond, source, actions))


  def start_tree(self, el):
    statechart = self.require("statechart")
    self.push("datamodel", statechart.datamodel)
    self.push("transitions", [])
    self.push("state_children", {})

  def end_tree(self, el):
    statechart = self.require("statechart")
    context = self.require("context")
    datamodel = self.pop("datamodel")

    root_states = self.pop("state_children")
    if len(root_states) == 0:
      raise Exception("Missing root <state> !")
    root = list(root_states.values())[0]

    # Add transitions.
    # Only now that our tree structure is complete can we resolve 'target' states of transitions.
    next_after_id = 0
    transitions = self.pop("transitions")
    for t_el, target_string, event, port, after, cond, source, actions in transitions:
      try:
        # Parse and find target state
        parse_tree = parse_state_ref(target_string)
      except Exception as e:
        self._raise(t_el, "Parsing target '%s': %s" % (target_string, str(e)))

      def find_state(sequence) -> State:
        if sequence.data == "relative_path":
          state = source
        elif sequence.data == "absolute_path":
          state = root
        for item in sequence.children:
          if item.type == "PARENT_NODE":
            state = state.parent
          elif item.type == "CURRENT_NODE":
            continue
          elif item.type == "IDENTIFIER":
            state = [x for x in state.children if x.short_name == item.value][0]
        return state

      try:
        targets = [find_state(seq) for seq in parse_tree.children]
      except:
        self._raise(t_el, "Could not find target '%s'." % (target_string))

      transition = Transition(source, targets)

      # Trigger
      if after is not None:
        after_expr = parse_expression(context, datamodel, expr=after)
        # print(after_expr)
        event = "_after%d" % next_after_id # transition gets unique event name
        next_after_id += 1
        trigger = AfterTrigger(context.events.assign_id(event), event, after_expr)
      elif event is not None:
        trigger = Trigger(context.events.assign_id(event), event, port)
        context.inports.assign_id(port)
      else:
        trigger = None
      transition.trigger = trigger
      # Actions
      transition.actions = actions
      # Guard
      if cond is not None:
        try:
          expr = parse_expression(context, datamodel, expr=cond)
        except Exception as e:
          self._raise(t_el, "Condition '%s': %s" % (cond, str(e)))
        transition.guard = expr
      source.transitions.append(transition)

    statechart.tree = StateTree(root)


  def _internal_end_semantics(self, el):
    statechart = self.require("statechart")
    # Use reflection to find the possible XML attributes and their values
    for aspect in dataclasses.fields(Semantics):
      key = el.get(aspect.name)
      if key is not None:
        if key == "*":
          setattr(statechart.semantics, aspect.name, None)
        else:
          value = aspect.type[key.upper()]
          setattr(statechart.semantics, aspect.name, value)

  def end_semantics(self, el):
    self._internal_end_semantics(el)

  def end_override_semantics(self, el):
    self._internal_end_semantics(el)


  def start_statechart(self, el):
    src_file = self.require("src_file")
    ext_file = el.get("src")
    if ext_file is None:
      statechart = Statechart(
        tree=None, semantics=Semantics(), datamodel=DataModel())
    else:
      ext_file_path = os.path.join(os.path.dirname(src_file), ext_file)
      self.push("statecharts", [])
      self.parse(ext_file_path)
      statecharts = self.pop("statecharts")
      if len(statecharts) != 1:
        raise Exception("Expected exactly 1 <statechart> node, got %d." % len(statecharts))
      statechart = statecharts[0]
    self.push("statechart", statechart)

  def end_statechart(self, el):
    statecharts = self.require("statecharts")
    sc = self.pop("statechart")
    statecharts.append(sc)
