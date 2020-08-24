from typing import *
from lark.exceptions import *
from sccd.statechart.static.statechart import *
from sccd.statechart.static.tree import *
from sccd.statechart.dynamic.builtin_scope import *
from sccd.util.xml_parser import *
from sccd.statechart.parser.text import *

class SkipFile(Exception):
  pass

parse_f = functools.partial(parse, decorate_exceptions=(ModelError,LarkError))

def check_duration_type(type):
  if type != SCCDDuration:
    msg = "Expression is '%s' type. Expected 'Duration' type." % str(type)
    if type == SCCDInt:
      msg += "\n Hint: Did you forget a duration unit suffix? ('s', 'ms', ...)"
    raise XmlError(msg)

# path: filesystem path for finding external statecharts
def statechart_parser_rules(globals, path, load_external = True, parse_f = parse_f) -> Rules:
  import os
  def parse_statechart(el):
    ext_file = el.get("src")
    if ext_file is None:
      statechart = Statechart(
        semantics=SemanticConfiguration(),
        scope=Scope("instance", parent=BuiltIn),
        datamodel=None,
        internal_events=Bitmap(),
        internally_raised_events=Bitmap(),
        inport_events={},
        event_outport={},
        tree=None,
      )
    else:
      if not load_external:
        raise SkipFile("Parser configured not to load statecharts from external files.")
      statechart = parse_f(os.path.join(path, ext_file), [("statechart", statechart_parser_rules(globals, path, load_external=False, parse_f=parse_f))])

    def parse_semantics(el):
      # Use reflection to find the possible XML attributes and their values
      for aspect_name, aspect_type in SemanticConfiguration.get_fields():
        def parse_semantic_attribute(text):
          result = parse_semantic_choice(text)
          if result.data == "wildcard":
            semantic_choice = list(aspect_type) # all options
          elif result.data == "list":
            semantic_choice = [aspect_type[token.value.upper()] for token in result.children]
          if len(semantic_choice) == 1:
            semantic_choice = semantic_choice[0]
          setattr(statechart.semantics, aspect_name, semantic_choice)

        if_attribute(el, aspect_name, parse_semantic_attribute)

    def parse_datamodel(el):
      body = parse_block(globals, el.text)
      body.init_stmt(statechart.scope)
      statechart.datamodel = body

    def parse_inport(el):
      port_name = require_attribute(el, "name")
      globals.inports.assign_id(port_name)
      def parse_event(el):
        event_name = require_attribute(el, "name")
        event_id = globals.events.assign_id(event_name)
        port_events = statechart.inport_events.setdefault(port_name, Bitmap())
        port_events |= bit(event_id)
        statechart.inport_events[port_name] = port_events
        statechart.internal_events |= bit(event_id)
      return [("event+", parse_event)]

    def parse_outport(el):
      port_name = require_attribute(el, "name")
      def parse_event(el):
        event_name = require_attribute(el, "name")
        statechart.event_outport[event_name] = port_name
      return [("event+", parse_event)]

    def parse_root(el):
      if el.get("id") is not None:
        raise XmlError("<root> state must not have 'id' attribute.")
      root = State("", parent=None)
      children_dict = {}
      transitions = [] # All of the statechart's transitions accumulate here, cause we still need to find their targets, which we can't do before the entire state tree has been built. We find their targets when encoutering the </root> closing tag.
      after_id = 0 # After triggers need unique IDs within the scope of the statechart model

      def actions_rules(scope):

        def parse_raise(el):
          params = []
          def parse_param(el):
            expr_text = require_attribute(el, "expr")
            expr = parse_expression(globals, expr_text)
            expr.init_expr(scope)
            params.append(expr)

          def finish_raise():
            event_name = require_attribute(el, "event")
            try:
              port = statechart.event_outport[event_name]
            except KeyError:
              # Legacy fallback: read port from attribute
              port = el.get("port")
            if port is None:
              # internal event
              event_id = globals.events.assign_id(event_name)
              statechart.internally_raised_events |= bit(event_id)
              return RaiseInternalEvent(event_id=event_id, name=event_name, params=params)
            else:
              # output event - no ID in global namespace
              statechart.event_outport[event_name] = port
              globals.outports.assign_id(port)
              return RaiseOutputEvent(name=event_name, params=params, outport=port)
          return ([("param*", parse_param)], finish_raise)

        def parse_code(el):
          def finish_code():
            block = parse_block(globals, el.text)
            # local_scope = Scope("local", scope)
            block.init_stmt(scope)
            return Code(block)
          return ([], finish_code)

        return {"raise": parse_raise, "code": parse_code}

      def deal_with_initial(el, state, children_dict):
        have_initial = False

        def parse_attr_initial(initial):
          nonlocal have_initial
          have_initial = True
          try:
            state.default_state = children_dict[initial]
          except KeyError as e:
            raise XmlError("Not a child.") from e

        if_attribute(el, "initial", parse_attr_initial)

        if not have_initial:
          if len(state.children) == 1:
            state.default_state = state.children[0]
          elif len(state.children) > 1:
            raise XmlError("More than 1 child state: must set 'initial' attribute.")

      def state_child_rules(parent, sibling_dict: Dict[str, State]):

        def common(el, constructor):
          short_name = require_attribute(el, "id")
          if short_name == "":
            raise XmlError("attribute 'id' must be non-empty string")
          state = constructor(short_name, parent)

          already_there = sibling_dict.setdefault(short_name, state)
          if already_there is not state:
            raise XmlError("Sibling state with the same id exists.")
          return state

        def common_nonpseudo(el, constructor):
          state = common(el, constructor)
          if el.get("stable", "") == "true":
            state.stable = True
          return state

        def parse_state(el):
          state = common_nonpseudo(el, State)
          children_dict = {}
          def finish_state():
            deal_with_initial(el, state, children_dict)
          return (state_child_rules(parent=state, sibling_dict=children_dict), finish_state)

        def parse_parallel(el):
          state = common_nonpseudo(el, ParallelState)
          return state_child_rules(parent=state, sibling_dict={})

        def parse_history(el):
          history_type = el.get("type", "shallow")
          if history_type == "deep":
            common(el, DeepHistoryState)
          elif history_type == "shallow":
            common(el, ShallowHistoryState)
          else:
            raise XmlError("attribute 'type' must be \"shallow\" or \"deep\".")

        def parse_onentry(el):
          def finish_onentry(*actions):
            parent.enter = actions
          return (actions_rules(statechart.scope), finish_onentry)

        def parse_onexit(el):
          def finish_onexit(*actions):
            parent.exit = actions
          return (actions_rules(statechart.scope), finish_onexit)

        def parse_transition(el):
          if parent is root:
            raise XmlError("Root cannot be source of a transition.")

          scope = Scope("event_params", parent=statechart.scope)
          target_string = require_attribute(el, "target")
          transition = Transition(parent, [], scope, target_string)

          have_event_attr = False
          def parse_attr_event(event):
            nonlocal have_event_attr
            have_event_attr = True

            positive_events, negative_events = parse_events_decl(globals, event)

            # Optimization: sort events by ID
            # Allows us to save time later.
            positive_events.sort(key=lambda e: e.id)

            def add_params_to_scope(e: EventDecl):
              for i,p in enumerate(e.params_decl):
                p.init_param(scope)

            for e in itertools.chain(positive_events, negative_events):
              add_params_to_scope(e)

            if not negative_events:
              transition.trigger = Trigger(positive_events)
              statechart.internal_events |= transition.trigger.enabling_bitmap
            else:
              transition.trigger = NegatedTrigger(positive_events, negative_events)
              statechart.internal_events |= transition.trigger.enabling_bitmap

          def parse_attr_after(after):
            nonlocal after_id
            if have_event_attr:
              raise XmlError("Cannot specify 'after' and 'event' at the same time.")
            after_expr = parse_expression(globals, after)
            after_type = after_expr.init_expr(scope)
            check_duration_type(after_type)
            # after-events should only be generated by the runtime
            # by putting a '+' in the event name (which isn't an allowed character in the parser),
            # we can be certain that the user will never generate a valid after-event.
            if DEBUG:
              event_name = "+%d_%s_%s" % (after_id, parent.short_name, target_string) # transition gets unique event name
            else:
              event_name = "+%d" % after_id
            transition.trigger = AfterTrigger(globals.events.assign_id(event_name), event_name, after_id, after_expr)
            after_id += 1

          def parse_attr_cond(cond):
            expr = parse_expression(globals, cond)
            guard_type = expr.init_expr(scope)
            if guard_type is not SCCDBool:
              raise XmlError("Guard should be an expression evaluating to 'bool'.")
            transition.guard = expr

          if_attribute(el, "event", parse_attr_event)
          if_attribute(el, "after", parse_attr_after)
          if_attribute(el, "cond", parse_attr_cond)

          def finish_transition(*actions):
            transition.actions = actions
            transitions.append((transition, el))
            parent.transitions.append(transition)

          return (actions_rules(scope), finish_transition)

        return {"state": parse_state, "parallel": parse_parallel, "history": parse_history, "onentry": parse_onentry, "onexit": parse_onexit, "transition": parse_transition}

      def finish_root():
        deal_with_initial(el, root, children_dict)

        for transition, t_el in transitions:
          try:
            parse_tree = parse_state_ref(transition.target_string)
          except Exception as e:
            raise XmlErrorElement(t_el, "Parsing target '%s': %s" % (transition.target_string, str(e))) from e

          def find_target(sequence) -> State:
            if sequence.data == "relative_path":
              state = transition.source
            elif sequence.data == "absolute_path":
              state = root
            for item in sequence.children:
              if item.type == "PARENT_NODE":
                state = state.parent
              elif item.type == "CURRENT_NODE":
                continue
              elif item.type == "IDENTIFIER":
                state = [x for x in state.children if x.short_name == item.value][0]
            if state is root:
              raise XmlError("Root cannot be target of a transition.")
            return state

          try:
            transition.targets = [find_target(seq) for seq in parse_tree.children]
          except Exception as e:
            raise XmlErrorElement(t_el, "target=\"%s\": %s" % (transition.target_string, str(e))) from e

        statechart.tree = optimize_tree(root)

      return (state_child_rules(root, sibling_dict=children_dict), finish_root)

    def finish_statechart():
      return statechart

    if ext_file is None:
      return ([("semantics?", parse_semantics), ("datamodel?", parse_datamodel), ("inport*", parse_inport), ("outport*", parse_outport), ("root", parse_root)], finish_statechart)
    else:
      return ([("override_semantics?", parse_semantics)], finish_statechart)

  return parse_statechart
