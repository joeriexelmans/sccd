import dataclasses
from lxml import etree
from sccd.parser.expression_parser import *
from sccd.syntax.statechart import *
from sccd.syntax.tree import *
from sccd.execution.event import *

# An Exception that occured while visiting an XML element.
# It will show a fragment of the source file and the line number of the error.
class XmlLoadError(Exception):
  def __init__(self, src_file: str, el: etree.Element, msg):
    parent = el.getparent()
    if parent is None:
      parent = el

    lines = etree.tostring(parent).decode('utf-8').strip().split('\n')
    nbr_highlighted_lines = len(etree.tostring(el).decode('utf-8').strip().split('\n'))
    text = []

    parent_firstline = parent.sourceline
    parent_lastline = parent.sourceline + len(lines) - 1

    el_firstline = el.sourceline
    el_lastline = el.sourceline + nbr_highlighted_lines - 1

    numbered_lines = list(zip(range(parent.sourceline, parent.sourceline + len(lines)), lines))

    from_line = max(parent_firstline, el_firstline - 5)
    to_line = min(parent_lastline, el_lastline + 5)

    if from_line == parent_firstline+1:
      from_line = parent_firstline
    if to_line == parent_lastline-1:
      to_line = parent_lastline

    def f(tup):
      return from_line <= tup[0] <= to_line

    if from_line != parent_firstline:
      text.append("%4d: %s" % (parent_firstline, lines[0]))
      text.append("     ...")

    for linenumber, line in filter(f, numbered_lines):
      ll = "%4d: %s" % (linenumber, line)
      if el_firstline <= linenumber <= el_lastline:
        ll = termcolor.colored(ll, 'yellow')
      text.append(ll)

    if to_line != parent_lastline:
      text.append("     ...")
      text.append("%4d: %s" % (parent_lastline, lines[-1]))

    super().__init__("\n\n%s\n\n%s:\nline %d: <%s>: %s" % ('\n'.join(text), src_file,el.sourceline, el.tag, msg))
    
    # self.src_file = src_file
    # self.el = el
    # self.err = err


class XmlParser:

  # Stack-like data structure extensively used for event-driven parsing.
  # Typically, when visiting the opening tag of a parent XML element, a context value is *pushed*, and when visiting the matching closing tag, that value is popped. Child XML elements will be able to "peek" or, more often, "require" a context value to "be there". This way, child XML elements can express only being allowed as children of certain parent XML elements that push/pop these contexts, otherwise raising an exception.
  class Context:
    def __init__(self, name):
      self.data = []
      self.name = name

    def push(self, value):
      self.data.append(value)

    def pop(self):
      return self.data.pop()

    def peek(self, default=None):
      try:
        return self.data[-1]
      except IndexError:
        return default

    # Same as peek, but raises exception of stack is empty
    def require(self):
      try:
        return self.data[-1]
      except IndexError as e:
        raise Exception("Element expected only within context: %s" % self.name) from e


  def __init__(self):
    self.src_file = XmlParser.Context("src_file")

  def parse(self, src_file):
    self.src_file.push(src_file)

    for event, el in etree.iterparse(src_file, events=("start", "end")):
      # print(event, el.tag)
      try:
        if event == "start":
          start_method = getattr(self, "start_"+el.tag, None)
          if start_method:
            start_method(el)

        elif event == "end":
          end_method = getattr(self, "end_"+el.tag, None)
          if end_method:
            end_method(el)

      except XmlLoadError:
        raise
      except Exception as e:
        # An advantage of this event-driven parsing is that if an exception is thrown during the visiting of an XML node, we can automatically decorate it with info about the tag where the error occured, the line number in the source file, etc.
        self._raise(el, str(e), e)

      # We don't need anything from this element anymore, so we clear it to save memory.
      # This is a technique mentioned in the lxml documentation:
      # https://lxml.de/tutorial.html#event-driven-parsing
      # el.clear()
      # Currently disabled for 2 reasons:
      # 1) Because we store <transition> elements and need to read their attributes later on.
      # 2) To be able to pretty-print XML data later on, if a future error occurs.
      
    self.src_file.pop()

  def _raise(self, el, msg, err: Exception):
    src_file = self.src_file.require()
    raise XmlLoadError(src_file, el, msg) from err


# Parses action elements: <raise>, <code>
class ActionParser(XmlParser):

  def __init__(self):
    super().__init__()
    self.globals = XmlParser.Context("globals")
    self.datamodel = XmlParser.Context("datamodel")
    self.actions = XmlParser.Context("actions")

  def end_raise(self, el):
    globals = self.globals.require()
    actions = self.actions.require()

    name = el.get("event")
    port = el.get("port")
    if not port:
      event_id = globals.events.assign_id(name)
      a = RaiseInternalEvent(name=name, parameters=[], event_id=event_id)
    else:
      globals.outports.assign_id(port)
      a = RaiseOutputEvent(name=name, parameters=[], outport=port, time_offset=0)
    actions.append(a)

  def end_code(self, el):
    globals = self.globals.require()
    datamodel = self.datamodel.require()
    actions = self.actions.require()

    block = parse_block(globals, datamodel, block=el.text)
    a = Code(block)
    actions.append(a)

# Parses state elements: <state>, <parallel>, <history>,
# and all its children (transitions, entry/exit actions)
class StateParser(ActionParser):

  def __init__(self):
    super().__init__()
    self.state = XmlParser.Context("state")
    self.state_children = XmlParser.Context("state_children")
    self.transitions = XmlParser.Context("transitions")

  def _internal_start_state(self, el, constructor):
    parent = self.state.peek(default=None)

    short_name = el.get("id", "")
    if parent is None:
      if short_name:
        raise Exception("Root <state> must not have 'id' attribute.")
    else:
      if not short_name:
        raise Exception("Non-root <state> must have 'id' attribute.")

    state = constructor(short_name, parent)

    parent_children = self.state_children.require()
    already_there = parent_children.setdefault(short_name, state)
    if already_there is not state:
      if parent:
        raise Exception("Sibling state with the same id exists.")
      else:
        raise Exception("Only 1 root <state> allowed.")

    self.state.push(state)
    self.state_children.push({})

  def _internal_end_state(self):
    state_children = self.state_children.pop()
    state = self.state.pop()
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
    self.actions.push([])

  def end_onentry(self, el):
    actions = self.actions.pop()
    self.state.require().enter = actions

  def start_onexit(self, el):
    self.actions.push([])

  def end_onexit(self, el):
    actions = self.actions.pop()
    self.state.require().exit = actions

  def start_transition(self, el):
    if self.state.require().parent is None:
      raise Exception("Root <state> cannot be source of a transition.")

    self.actions.push([])

  def end_transition(self, el):
    transitions = self.transitions.require()
    actions = self.actions.pop()
    source = self.state.require()

    # Parse <transition> element not until all states have been parsed,
    # and state tree constructed.
    transitions.append((el, source, actions))

# Parses <statechart> element and all its children.
class TreeParser(StateParser):

  def __init__(self):
    super().__init__()
    self.statechart = XmlParser.Context("statechart")


  # <tree>

  def start_tree(self, el):
    statechart = self.statechart.require()
    self.datamodel.push(statechart.datamodel)
    self.transitions.push([])
    self.state_children.push({})

  def end_tree(self, el):
    statechart = self.statechart.require()
    globals = self.globals.require()
    datamodel = self.datamodel.pop()

    root_states = self.state_children.pop()
    if len(root_states) == 0:
      raise Exception("Missing root <state> !")
    root = list(root_states.values())[0]

    # Add transitions.
    # Only now that our tree structure is complete can we resolve 'target' states of transitions.
    next_after_id = 0
    transitions = self.transitions.pop()
    for t_el, source, actions in transitions:
      target_string = t_el.get("target", "")
      event = t_el.get("event")
      port = t_el.get("port")
      after = t_el.get("after")
      cond = t_el.get("cond")

      try:
        # Parse and find target state
        parse_tree = parse_state_ref(target_string)
      except Exception as e:
        self._raise(t_el, "Parsing target '%s': %s" % (target_string, str(e)), e)

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
      except Exception as e:
        self._raise(t_el, "Could not find target '%s'." % (target_string), e)

      transition = Transition(source, targets)

      # Trigger
      if after is not None:
        after_expr = parse_expression(globals, datamodel, expr=after)
        # print(after_expr)
        event = "_after%d" % next_after_id # transition gets unique event name
        next_after_id += 1
        trigger = AfterTrigger(globals.events.assign_id(event), event, after_expr)
      elif event is not None:
        trigger = Trigger(globals.events.assign_id(event), event, port)
        globals.inports.assign_id(port)
      else:
        trigger = None
      transition.trigger = trigger
      # Actions
      transition.actions = actions
      # Guard
      if cond is not None:
        try:
          expr = parse_expression(globals, datamodel, expr=cond)
        except Exception as e:
          self._raise(t_el, "Condition '%s': %s" % (cond, str(e)), e)
        transition.guard = expr
      source.transitions.append(transition)

    statechart.tree = StateTree(root)

class StatechartParser(TreeParser):

  def __init__(self, load_external = True):
    super().__init__()
    self.load_external = load_external

    self.statecharts = XmlParser.Context("statecharts")

  # <semantics>

  def _internal_end_semantics(self, el):
    statechart = self.statechart.require()
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
    if self.load_external:
      self._internal_end_semantics(el)

  # <datamodel>

  def end_var(self, el):
    globals = self.globals.require()
    datamodel = self.datamodel.require()

    id = el.get("id")
    expr = el.get("expr")
    parsed = parse_expression(globals, datamodel, expr=expr)
    datamodel.create(id, parsed.eval([], datamodel))

  def start_datamodel(self, el):
    statechart = self.statechart.require()
    self.datamodel.push(statechart.datamodel)

  def end_datamodel(self, el):
    self.datamodel.pop()

  # <statechart>

  def start_statechart(self, el):
    src_file = self.src_file.require()
    ext_file = el.get("src")
    statechart = None
    if ext_file is None:
      statechart = Statechart(
        tree=None, semantics=Semantics(), datamodel=DataModel())
    elif self.load_external:
      ext_file_path = os.path.join(os.path.dirname(src_file), ext_file)
      self.statecharts.push([])
      self.parse(ext_file_path)
      statecharts = self.statecharts.pop()
      if len(statecharts) != 1:
        raise Exception("Expected exactly 1 <statechart> node, got %d." % len(statecharts))
      statechart = statecharts[0]
    self.statechart.push(statechart)

  def end_statechart(self, el):
    statecharts = self.statecharts.require()
    sc = self.statechart.pop()
    if sc is not None:
      statecharts.append(sc)
