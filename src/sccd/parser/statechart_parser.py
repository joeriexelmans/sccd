from typing import *
from sccd.syntax.statechart import *
from sccd.syntax.tree import *
from sccd.execution.builtin_scope import *
from sccd.parser.xml_parser import *
from sccd.parser.expression_parser import *

class SkipFile(Exception):
  pass

_blank_eval_context = EvalContext(current_state=None, events=[], memory=None)

parse_f = functools.partial(parse, decorate_exceptions=(ModelError,))

def create_statechart_parser(globals, src_file, load_external = True, parse = parse_f) -> Rules:
  def parse_statechart(el):
    ext_file = el.get("src")
    if ext_file is None:
      statechart = Statechart(
        semantics=SemanticConfiguration(),
        scope=Scope("instance", parent=BuiltIn),
        datamodel=None,
        inport_events={},
        event_outport={},
        tree=None,
      )
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
      body = parse_block(globals, el.text)
      body.init_stmt(statechart.scope)
      statechart.datamodel = body

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
      transitions = [] # All of the statechart's transitions accumulate here, cause we still need to find their targets, which we can't do before the entire state tree has been built. We find their targets when encoutering the </root> closing tag.
      next_after_id = 0 # Counter for 'after' transitions within the statechart.

      def create_actions_parser(scope):

        def parse_raise(el):
          params = []
          def parse_param(el):
            expr_text = require_attribute(el, "expr")
            expr = parse_expression(globals, expr_text)
            expr.init_rvalue(scope)
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
              return RaiseInternalEvent(name=event_name, params=params, event_id=event_id)
            else:
              # output event - no ID in global namespace
              globals.outports.assign_id(port)
              return RaiseOutputEvent(name=event_name, params=params, outport=port, time_offset=0)
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
        initial = el.get("initial")
        if initial is not None:
          try:
            state.default_state = children_dict[initial]
          except KeyError as e:
            raise XmlError("initial=\"%s\": not a child." % (initial)) from e
        elif len(state.children) == 1:
          state.default_state = state.children[0]
        elif len(state.children) > 1:
          raise XmlError("More than 1 child state: must set 'initial' attribute.")

      def create_state_parser(parent, sibling_dict: Dict[str, State]={}):

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
          def finish_state():
            deal_with_initial(el, state, children_dict)
          return (create_state_parser(parent=state, sibling_dict=children_dict), finish_state)

        def parse_parallel(el):
          state = common_nonpseudo(el, ParallelState)
          return create_state_parser(parent=state)

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
          return (create_actions_parser(statechart.scope), finish_onentry)

        def parse_onexit(el):
          def finish_onexit(*actions):
            parent.exit = actions
          return (create_actions_parser(statechart.scope), finish_onexit)

        def parse_transition(el):
          nonlocal next_after_id
          
          if parent is root:
            raise XmlError("Root <state> cannot be source of a transition.")

          scope = Scope("event_params", parent=statechart.scope)
          target_string = require_attribute(el, "target")
          transition = Transition(parent, [], scope, target_string)

          event = el.get("event")
          if event is not None:
            positive_events, negative_events = parse_events_decl(globals, event)

            # Optimization: sort events by ID
            # Allows us to save time later.
            positive_events.sort(key=lambda e: e.id)

            def add_event_params_to_scope(e: EventDecl):
              for i,p in enumerate(e.params_decl):
                p.init_param(scope)

            for e in itertools.chain(positive_events, negative_events):
              add_event_params_to_scope(e)

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
              if after_type != SCCDDuration:
                msg = "Expression is '%s' type. Expected 'Duration' type." % str(after_type)
                if after_type == SCCDInt:
                  msg += "\n Hint: Did you forget a duration unit sufix? ('s', 'ms', ...)"
                raise Exception(msg)
              event_name = "_after%d" % next_after_id # transition gets unique event name
              transition.trigger = AfterTrigger(globals.events.assign_id(event_name), event_name, next_after_id, after_expr)
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
              # raise except_msg("cond=\"%s\": " % cond, e)
            transition.guard = expr

          def finish_transition(*actions):
            transition.actions = actions
            transitions.append((transition, el))
            parent.transitions.append(transition)

          return (create_actions_parser(scope), finish_transition)

        return {"state": parse_state, "parallel": parse_parallel, "history": parse_history, "onentry": parse_onentry, "onexit": parse_onexit, "transition": parse_transition}

      def finish_root():
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

      return (create_state_parser(root, sibling_dict=children_dict), finish_root)

    def finish_statechart():
      return statechart

    return ([("semantics?", parse_semantics), ("override_semantics?", parse_semantics), ("datamodel?", parse_datamodel), ("inport*", parse_inport), ("outport*", parse_outport), ("root", parse_root)], finish_statechart)

  return [("statechart", parse_statechart)]
