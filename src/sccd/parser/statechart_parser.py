from typing import *
from sccd.syntax.statechart import *
from sccd.syntax.tree import *
from sccd.execution import builtin_scope
from sccd.parser.xml_parser import *
from sccd.parser.expression_parser import *

class SkipFile(Exception):
  pass

_blank_eval_context = EvalContext(current_state=None, events=[], memory=None)

def create_statechart_parser(globals, src_file, load_external = True) -> Rules:
  def parse_statechart(el):
    ext_file = el.get("src")
    if ext_file is None:
      statechart = Statechart(
        inport_events={},
        event_outport={},
        semantics=SemanticConfiguration(),
        tree=None,
        scope=Scope("instance", parent=builtin_scope.builtin_scope))
    else:
      if not load_external:
        raise SkipFile("Parser configured not to load statecharts from external files.")
      import os
      ext_file_path = os.path.join(os.path.dirname(src_file), ext_file)
      statechart = parse(ext_file_path, create_statechart_parser(globals, ext_file_path))

    def parse_semantics(el):
      # Use reflection to find the possible XML attributes and their values
      for aspect_name, aspect_type in SemanticConfiguration.get_fields():
        text = el.get(aspect_name)
        if text is not None:
          result = parse_semantic_choice(text)
          if result.data == "wildcard":
            semantic_choice = list(aspect_type) # all options
          elif result.data == "list":
            semantic_choice = [aspect_type[token.value.upper()] for token in result.children]
          if len(semantic_choice) == 1:
            semantic_choice = semantic_choice[0]
          setattr(statechart.semantics, aspect_name, semantic_choice)

    def parse_datamodel(el):
      def parse_var(el):
        id = el.get("id")
        expr = el.get("expr")

        parsed = parse_expression(globals, expr)
        rhs_type = parsed.init_rvalue(statechart.scope)
        val = parsed.eval(_blank_eval_context)
        statechart.scope.add_variable_w_initial(name=id, initial=val)

      def parse_func(el):
        id = el.get("id")
        text = el.text

        name, params = parse_func_decl(id)
        body = parse_block(globals, text)
        func = Function(params, body)
        func.init_stmt(statechart.scope)
        statechart.scope.add_function(name, func)

      return {"var": parse_var, "func": parse_func}

    def parse_inport(el):
      port_name = require_attribute(el, "name")
      def parse_event(el):
        event_name = require_attribute(el, "name")
        event_id = globals.events.assign_id(event_name)
        port_events = statechart.inport_events.setdefault(port_name, set())
        port_events.add(event_id)
      return [("event+", parse_event)]

    def parse_outport(el):
      port_name = require_attribute(el, "name")
      def parse_event(el):
        event_name = require_attribute(el, "name")
        statechart.event_outport[event_name] = port_name
      return [("event+", parse_event)]

    def parse_root(el):
      root = State("", parent=None)
      children_dict = {}
      transitions = []
      next_after_id = 0

      def create_actions_parser(scope):

        def parse_raise(el):
          params = []
          def parse_param(el):
            expr_text = require_attribute(el, "expr")
            expr = parse_expression(globals, expr_text)
            expr.init_rvalue(scope)
            params.append(expr)

          def when_done():
            event_name = require_attribute(el, "event")
            try:
              port = statechart.event_outport[event_name]
            except KeyError:
              # Legacy fallback: read port from attribute
              port = el.get("port")
            if port is None:
              # internal event
              event_id = globals.events.assign_id(event_name)
              return RaiseInternalEvent(name=event_name, params=params, event_id=event_id)
            else:
              # output event - no ID in global namespace
              globals.outports.assign_id(port)
              return RaiseOutputEvent(name=event_name, params=params, outport=port, time_offset=0)
          return ([("param*", parse_param)], when_done)

        def parse_code(el):
          def when_done():
            block = parse_block(globals, el.text)
            block.init_stmt(scope)
            return Code(block)
          return ([], when_done)

        return {"raise": parse_raise, "code": parse_code}

      def deal_with_initial(el, state, children_dict):
        initial = el.get("initial")
        if initial is not None:
          try:
            state.default_state = children_dict[initial]
          except KeyError as e:
            print("children:", children_dict.keys())
            raise XmlError("initial=\"%s\": not a child." % (initial)) from e
        elif len(state.children) == 1:
          state.default_state = state.children[0]
        elif len(state.children) > 1:
          raise XmlError("More than 1 child state: must set 'initial' attribute.")

      def create_state_parser(parent, sibling_dict):

        def common(el, constructor):
          short_name = require_attribute(el, "id")
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
          def when_done():
            deal_with_initial(el, state, children_dict)
          return (create_state_parser(parent=state, sibling_dict=children_dict), when_done)

        def parse_parallel(el):
          state = common_nonpseudo(el, ParallelState)
          return create_state_parser(parent=state, sibling_dict={})

        def parse_history(el):
          history_type = el.get("type", "shallow")
          if history_type == "deep":
            common(el, DeepHistoryState)
          elif history_type == "shallow":
            common(el, ShallowHistoryState)
          else:
            raise XmlError("attribute 'type' must be \"shallow\" or \"deep\".")

        def parse_onentry(el):
          def when_done(*actions):
            parent.enter = actions
          return (create_actions_parser(statechart.scope), when_done)

        def parse_onexit(el):
          def when_done(*actions):
            parent.exit = actions
          return (create_actions_parser(statechart.scope), when_done)

        def parse_transition(el):
          nonlocal next_after_id
          
          if parent is root:
            raise XmlError("Root <state> cannot be source of a transition.")

          target_string = require_attribute(el, "target")
          scope = Scope("transition", parent=statechart.scope)
          transition = Transition(parent, [], scope, target_string)

          event = el.get("event")
          if event is not None:
            positive_events, negative_events = parse_events_decl(globals, event)

            def process_event_decl(e: EventDecl):
              for i,p in enumerate(e.params):
                scope.add_event_parameter(event_name=e.name, param_name=p.name, type=p.type, param_offset=i)

            for e in itertools.chain(positive_events, negative_events):
              process_event_decl(e)

            if not negative_events:
              transition.trigger = Trigger(positive_events)
            else:
              transition.trigger = NegatedTrigger(positive_events, negative_events)

          after = el.get("after")
          if after is not None:
            if event is not None:
              raise XmlError("Cannot specify 'after' and 'event' at the same time.")
            try:
              after_expr = parse_expression(globals, after)
              after_type = after_expr.init_rvalue(scope)
              if after_type != Duration:
                msg = "Expression is '%s' type. Expected 'Duration' type." % str(after_type)
                if after_type == int:
                  msg += "\n Hint: Did you forget a duration unit sufix? ('s', 'ms', ...)"
                raise Exception(msg)
              event = "_after%d" % next_after_id # transition gets unique event name
              transition.trigger = AfterTrigger(globals.events.assign_id(event), event, next_after_id, after_expr)
              next_after_id += 1
            except Exception as e:
              raise XmlError("after=\"%s\": %s" % (after, str(e))) from e

          cond = el.get("cond")
          if cond is not None:
            try:
              expr = parse_expression(globals, cond)
              expr.init_rvalue(scope)
            except Exception as e:
              raise XmlError("cond=\"%s\": %s" % (cond, str(e))) from e
            transition.guard = expr

          def when_done(*actions):
            transition.actions = actions
            transitions.append((transition, el))
            parent.transitions.append(transition)

          return (create_actions_parser(scope), when_done)

        return {"state": parse_state, "parallel": parse_parallel, "history": parse_history, "onentry": parse_onentry, "onexit": parse_onexit, "transition": parse_transition}

      def when_done():
        deal_with_initial(el, root, children_dict)

        for transition, t_el in transitions:
          try:
            parse_tree = parse_state_ref(transition.target_string)
          except Exception as e:
            raise XmlErrorElement(t_el, "Parsing target '%s': %s" % (target_string, str(e))) from e

          def find_state(sequence) -> State:
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
            return state

          try:
            transition.targets = [find_state(seq) for seq in parse_tree.children]
          except Exception as e:
            raise XmlErrorElement(t_el, "Could not find target '%s'." % (transition.target_string)) from e

        statechart.tree = StateTree(root)

      return (create_state_parser(root, sibling_dict=children_dict), when_done)

    def when_done():
      return statechart

    return ([("semantics?", parse_semantics), ("override_semantics?", parse_semantics), ("datamodel?", parse_datamodel), ("inport*", parse_inport), ("outport*", parse_outport), ("root", parse_root)], when_done)

  return [("statechart", parse_statechart)]
