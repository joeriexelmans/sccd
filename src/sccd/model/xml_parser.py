from lxml import etree
from sccd.model.context import *
from sccd.model.parser import *
from sccd.syntax.tree import *

class XmlLoadError(Exception):
  def __init__(self, el: etree.Element, err: Exception):
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
    super().__init__("\n\n%s\n\nLine %d: <%s>: %s" % ('\n'.join(lines_numbers), el.sourceline, el.tag, str(err)))

class ElementHandler:

  def _get_stack(self, name):
    stack = getattr(self, name, None)
    if stack is None:
      stack = []
      setattr(self, name, stack)
    return stack

  def push(self, name, value):
    stack = self._get_stack(name)
    stack.append(value)

  def pop(self, name):
    stack = getattr(self, name)
    return stack.pop()

  def top(self, name, default=None):
    stack = getattr(self, name, [])
    return stack[-1] if len(stack) else default

  def all(self, name):
    stack = self._get_stack(name)
    return stack

class TreeHandler(ElementHandler):

  def __init__(self, context, datamodel):
    self.context = context
    self.datamodel = datamodel

  def end_raise(self, el):
    name = el.get("event")
    port = el.get("port")
    if not port:
      event_id = self.context.events.assign_id(name)
      a = RaiseInternalEvent(name=name, parameters=[], event_id=event_id)
    else:
      self.context.outports.assign_id(port)
      a = RaiseOutputEvent(name=name, parameters=[], outport=port, time_offset=0)
    self.top("actions").append(a)
    return a

  def end_code(self, el):
    block = parse_block(self.context, self.datamodel, block=el.text)
    a = Code(block)
    self.top("actions").append(a)
    return a

  def _start_state(self, el, constructor):
    parent = self.top("state", default=None)

    short_name = el.get("id", "")
    if parent is None:
      if short_name:
        raise XmlLoadError(el, "Root <state> must not have 'id' attribute.")
    else:
      if not short_name:
        raise XmlLoadError(el, "Non-root <state> must have 'id' attribute.")

    state = constructor(short_name, parent)

    parent_children = self.top("state_children")
    already_there = parent_children.setdefault(short_name, state)
    if already_there is not state:
      if parent:
        raise XmlLoadError(el, "Sibling state with the same id exists.")
      else:
        raise XmlLoadError(el, "Only 1 root <state> allowed.")

    self.push("state", state)
    self.push("state_children", {})

  def _end_state(self):
    # self.pop("state_prefix")
    state_children = self.pop("state_children")
    state = self.pop("state")
    return (state, state_children)

  def start_state(self, el):
    self._start_state(el, State)

  def end_state(self, el):
    state, state_children = self._end_state()

    initial = el.get("initial", None)
    if initial is not None:
      state.default_state = state_children[initial]
    elif len(state.children) == 1:
      state.default_state = state.children[0]
    elif len(state.children) > 1:
      raise XmlLoadError(el, "More than 1 child state: must set 'initial' attribute.")

  def start_parallel(self, el):
    self._start_state(el, ParallelState)

  def end_parallel(self, el):
    self._end_state()

  def start_history(self, el):
    if el.get("type", "shallow") == "deep":
      self._start_state(el, DeepHistoryState)
    else:
      self._start_state(el, ShallowHistoryState)

  def end_history(self, el):
    return self._end_state()

  def start_onentry(self, el):
    self.push("actions", [])

  def end_onentry(self, el):
    actions = self.pop("actions")
    self.top("state").enter = actions

  def start_onexit(self, el):
    self.push("actions", [])

  def end_onexit(self, el):
    actions = self.pop("actions")
    self.top("state").exit = actions

  def start_transition(self, el):
    self.push("actions", [])

  def end_transition(self, el):
    actions = self.pop("actions")
    # simply accumulate transition elements
    # we'll deal with them in end_tree()
    source = self.top("state")

    # get stuff from element
    target = el.get("target", "")
    event = el.get("event")
    port = el.get("port")
    after = el.get("after")
    cond = el.get("cond")

    self.top("transitions").append((el, target, event, port, after, cond, source, actions))


  def start_tree(self, el):
    # self.push("tree", StateTree())
    self.push("transitions", [])
    self.push("state_children", {})

  def end_tree(self, el):
    root_states = self.pop("state_children")
    if len(root_states) == 0:
      raise XmlLoadError(el, "Missing root <state> !")
    root = list(root_states.values())[0]

    transitions = self.pop("transitions")

    # Add transitions.
    # Only now that our tree structure is complete can we resolve 'target' states of transitions.
    next_after_id = 0
    for t_el, target_string, event, port, after, cond, source, actions in transitions:
      try:
        # Parse and find target state
        parse_tree = parse_state_ref(target_string)
      except Exception as e:
        raise XmlLoadError(t_el, "Parsing target '%s': %s" % (target_string, str(e)))

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
        raise XmlLoadError(t_el, "Could not find target '%s'." % (target_string))

      transition = Transition(source, targets)

      # Trigger
      if after is not None:
        after_expr = parse_expression(self.context, self.datamodel, expr=after)
        # print(after_expr)
        event = "_after%d" % next_after_id # transition gets unique event name
        next_after_id += 1
        trigger = AfterTrigger(self.context.events.assign_id(event), event, after_expr)
      elif event is not None:
        trigger = Trigger(self.context.events.assign_id(event), event, port)
        self.context.inports.assign_id(port)
      else:
        trigger = None
      transition.trigger = trigger
      # Actions
      transition.actions = actions
      # Guard
      if cond is not None:
        try:
          expr = parse_expression(self.context, self.datamodel, expr=cond)
        except Exception as e:
          raise XmlLoadError(t_el, "Condition '%s': %s" % (cond, str(e)))
        transition.guard = expr
      source.transitions.append(transition)

    self.tree = StateTree(root)

  def start_datamodel(self, el):
    pass

def parse(event_generator, handler: ElementHandler):
  # for event, el in etree.iterparse(file, events=("start", "end")):
  for event, el in event_generator:

    try:

      if event == "start":
        start_method = getattr(handler, "start_"+el.tag, None)
        if start_method:
          start_method(el)

      elif event == "end":
        end_method = getattr(handler, "end_"+el.tag)
        if end_method:
          end_method(el)

    except XmlLoadError:
      raise
    # Decorate non-XmlLoadErrors
    except Exception as e:
      raise XmlLoadError(el, e)

      # We don't need anything from this element anymore, so we clear it to save memory.
      # This is a technique mentioned in the lxml documentation:
      # https://lxml.de/tutorial.html#event-driven-parsing
      # el.clear()
