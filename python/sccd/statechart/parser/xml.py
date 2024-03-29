from typing import *
import re
from lark.exceptions import *
from sccd.statechart.static.types import *
from sccd.statechart.static.statechart import *
from sccd.statechart.static.tree import *
from sccd.statechart.dynamic.builtin_scope import *
from sccd.util.xml_parser import *
from sccd.statechart.parser.text import *
from sccd.statechart.static.in_state import InStateMacroExpansion

class SkipFile(Exception):
  pass

parse_f = functools.partial(parse, decorate_exceptions=(ModelStaticError,LarkError))

def check_duration_type(type):
  if type != SCCDDuration:
    msg = "Expression is '%s' type. Expected 'Duration' type." % str(type)
    if type == SCCDInt:
      msg += "\n Hint: Did you forget a duration unit suffix? ('s', 'ms', ...)"
    raise XmlError(msg)

# path: filesystem path for finding external statecharts
def statechart_parser_rules(globals, path, load_external = True, parse_f = parse_f, text_parser=TextParser(globals)) -> Rules:

  import os
  def parse_statechart(el):
    ext_file = el.get("src")
    if ext_file is None:
      statechart = Statechart(scope=Scope("statechart", parent=None))
    else:
      if not load_external:
        raise SkipFile("Parser configured not to load statecharts from external files.")
      statechart = parse_f(os.path.join(path, ext_file), [("statechart", statechart_parser_rules(globals, path, load_external=False, parse_f=parse_f, text_parser=text_parser))])

    def parse_semantics(el):
      available_aspects = SemanticConfiguration.get_fields()
      for aspect_name, text in el.attrib.items():
        try:
          aspect_type = available_aspects[aspect_name]
        except KeyError:
          raise XmlError("invalid semantic aspect: '%s'" % aspect_name)
        result = text_parser.parse_semantic_choice(text)
        if result.data == "wildcard":
          semantic_choice = list(aspect_type) # all options
        elif result.data == "list":
          semantic_choice = [aspect_type[token.value.upper()] for token in result.children]
        if len(semantic_choice) == 1:
          semantic_choice = semantic_choice[0]
        setattr(statechart.semantics, aspect_name, semantic_choice)

    def parse_datamodel(el):
      body = text_parser.parse_block(el.text)
      body.init_stmt(statechart.scope)
      statechart.datamodel = body

    def parse_event_param(el):
      type_text = require_attribute(el, "type")
      param_type = text_parser.parse_type(type_text)
      def finish_param():
        return param_type
      return ([], finish_param)

    def get_port_parser(add_to):
      def parse_port(el):
        def parse_event(el):
          event_name = require_attribute(el, "name")
          if event_name in add_to:
            raise XmlError("event already declared earlier: %s" % event_name)
          def finish_event(*params):
            add_to[event_name] = list(params)
          return ([("param*", parse_event_param)], finish_event)
        return [("event*", parse_event)]
      return parse_port

    def parse_root(el):
      if el.get("id") is not None:
        raise XmlError("<root> state must not have 'id' attribute.")
      root = State("", parent=None)
      children_dict = {}
      transitions = [] # All of the statechart's transitions accumulate here, cause we still need to find their targets, which we can't do before the entire state tree has been built. We find their targets when encoutering the </root> closing tag.
      after_id = 0 # After triggers need unique IDs within the scope of the statechart model
      refs_to_resolve = [] # Transition targets and INSTATE arguments. Resolved after constructing state tree.

      def get_default_state(el, state, children_dict):
        have_initial = False

        def parse_attr_initial(initial):
          nonlocal default_state
          nonlocal have_initial
          default_state = None
          have_initial = True
          try:
            default_state = children_dict[initial]
          except KeyError as e:
            raise XmlError("Not a child.") from e

        if_attribute(el, "initial", parse_attr_initial)

        if not have_initial:
          if len(state.children) == 1:
            default_state = state.children[0]
          else:
            raise XmlError("More than 1 child state: must set 'initial' attribute.")

        return default_state

      def state_child_rules(parent, sibling_dict: Dict[str, State]):

        # A transition's guard expression and action statements can read the transition's event parameters, and also possibly the current state configuration. We therefore now wrap these into a function with a bunch of parameters for those values that we want to bring into scope.
        def wrap_transition_params(expr_or_stmt, transition: Transition):
          if isinstance(expr_or_stmt, Statement):
            # Transition's action code
            body = expr_or_stmt
          elif isinstance(expr_or_stmt, Expression):
            # Transition's guard
            body = ReturnStatement(expr=expr_or_stmt)
          else:
            raise Exception("Unexpected error in parser")
          # The joy of writing expressions in abstract syntax:
          if transition is None:
            wrapped = FunctionDeclaration(params_decl=[], body=body)
          else:
            wrapped = FunctionDeclaration(
              params_decl=
                # The param '@conf' (which, on purpose, is an illegal identifier in textual concrete syntax, to prevent naming collisions) will contain the statechart's configuration as a bitmap (SCCDInt). This parameter is currently only used in the expansion of the INSTATE-macro.
                [ParamDecl(name="@conf", formal_type=SCCDStateConfiguration(state=parent))]
                # Plus all the parameters of the enabling events of the transition's trigger:
                + [param for event in transition.trigger.enabling for param in event.params_decl],
              body=body)
          return wrapped

        def actions_rules(scope, transition: Transition=None):

          def parse_raise(el):
            event_name = require_attribute(el, "event")
            params = []
            def parse_param(el):
              # Every event parameter becomes a function, with the event trigger's parameters as parameters
              expr_text = require_attribute(el, "expr")
              expr = text_parser.parse_expr(expr_text)
              function = wrap_transition_params(expr, transition=transition)
              function.init_expr(scope)
              function.scope.name = "event_param"
              params.append(function)

            def finish_raise():
              param_types = [p.return_type for p in params]
              try:
                formal_param_types = statechart.out_events[event_name]
                result = RaiseOutputEvent(name=event_name, params=params)
              except KeyError:
                try:
                  formal_param_types = statechart.internal_events[event_name]
                except KeyError:
                  formal_param_types = param_types
                  statechart.internal_events[event_name] = formal_param_types
                result = RaiseInternalEvent(name=event_name, params=params)
              if param_types != formal_param_types:
                raise XmlError("Event '%s': Parameter types %s don't match earlier %s" % (event_name, param_types, formal_param_types))
              return result
            return ([("param*", parse_param)], finish_raise)

          def parse_code(el):
            def finish_code():
              # Every block of code becomes a function, with the event trigger's parameters as parameters
              block = text_parser.parse_block(el.text)
              function = wrap_transition_params(block, transition=transition)
              function.init_expr(scope)
              function.scope.name = "code"
              return Code(function)
            return ([], finish_code)

          return {"raise": parse_raise, "code": parse_code}

        def common(el, constructor):
          short_name = require_attribute(el, "id")
          match = re.match("[A-Za-z_][A-Za-z_0-9]*", short_name)
          if match is None or match[0] != short_name:
            raise XmlError("invalid id")
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
            if len(state.children) > 0:
              state.type = OrState(state=state,
                default_state=get_default_state(el, state, children_dict))
            else:
              state.type = AndState(state=state)
          return (state_child_rules(parent=state, sibling_dict=children_dict), finish_state)

        def parse_parallel(el):
          state = common_nonpseudo(el, State)
          state.type = AndState(state=state)
          return state_child_rules(parent=state, sibling_dict={})

        def parse_history(el):
          history_type = el.get("type", "shallow")
          if history_type == "deep":
            state = common(el, DeepHistoryState)
          elif history_type == "shallow":
            state = common(el, ShallowHistoryState)
          else:
            raise XmlError("attribute 'type' must be \"shallow\" or \"deep\".")

        def parse_onentry(el):
          def finish_onentry(*actions):
            parent.enter = actions
          return (actions_rules(scope=statechart.scope), finish_onentry)

        def parse_onexit(el):
          def finish_onexit(*actions):
            parent.exit = actions
          return (actions_rules(scope=statechart.scope), finish_onexit)

        def parse_transition(el):

          def macro_in_state(params):
            if len(params) != 1:
              raise XmlError("Macro @in: Expected 1 parameter")
            ref= StateRef(source=parent, path=text_parser.parse_path(params[0].string))
            refs_to_resolve.append(ref)
            return InStateMacroExpansion(ref=ref)

          # INSTATE-macro allowed in transition's guard and actions
          text_parser.parser.options.transformer.set_macro("@in", macro_in_state)

          if parent is root:
            raise XmlError("Root cannot be source of a transition.")

          target_string = require_attribute(el, "target")

          try:
            path = text_parser.parse_path(target_string)
          except Exception as e:
            raise XmlErrorElement(t_el, "Parsing target '%s': %s" % (transition.target_string, str(e))) from e

          transition = Transition(source=parent, path=path)
          refs_to_resolve.append(transition)

          have_event_attr = False
          def parse_attr_event(event):
            nonlocal have_event_attr
            have_event_attr = True

            positive_events, negative_events = text_parser.parse_events_decl(event)

            if not negative_events:
              transition.trigger = Trigger(positive_events)
            else:
              transition.trigger = NegatedTrigger(positive_events, negative_events)

          def parse_attr_after(after):
            nonlocal after_id
            if have_event_attr:
              raise XmlError("Cannot specify 'after' and 'event' at the same time.")
            after_expr = text_parser.parse_expr(after)
            after_type = after_expr.init_expr(statechart.scope)
            check_duration_type(after_type)
            # After-events should only be generated by the runtime.
            # By putting a '+' in the event name (which isn't an allowed character in the parser), we ensure that the user will never accidentally (careless) or purposefully (evil) generate a valid after-event.
            event_name = "+%d" % after_id
            statechart.in_events[event_name] = []
            transition.trigger = AfterTrigger(event_name, after_id, after_expr)
            after_id += 1

          def parse_attr_cond(cond):
            # Transition's guard expression
            guard_expr = text_parser.parse_expr(cond)
            guard_function = wrap_transition_params(expr_or_stmt=guard_expr, transition=transition)
            guard_type = guard_function.init_expr(statechart.scope)
            guard_function.scope.name = "guard"

            if guard_type.return_type is not SCCDBool:
              raise XmlError("Guard should be an expression evaluating to 'bool'.")

            transition.guard = guard_function

          if_attribute(el, "event", parse_attr_event)
          if_attribute(el, "after", parse_attr_after)
          if_attribute(el, "cond", parse_attr_cond)

          def finish_transition(*actions):
            transition.actions = actions
            transitions.append((transition, el))
            parent.transitions.append(transition)
            # INSTATE-macro not allowed outside of transition's guard or actions
            text_parser.parser.options.transformer.unset_macro("@in")

          return (actions_rules(scope=statechart.scope, transition=transition), finish_transition)

        return {"state": parse_state, "parallel": parse_parallel, "history": parse_history, "onentry": parse_onentry, "onexit": parse_onexit, "transition": parse_transition}

      def finish_root():
        root.type = OrState(state=root, default_state=get_default_state(el, root, children_dict))

        # State tree has been constructed, we can now resolve state refs:
        for ref in refs_to_resolve:
          try:
            ref.resolve(root=root)
          except PathError as e:
            raise XmlErrorElement(t_el, "target=\"%s\": %s" % (transition.target_string, str(e))) from e

        # Next, visit tree to statically calculate many properties of states and transitions:
        statechart.tree = StateTree(root)

      return (state_child_rules(root, sibling_dict=children_dict), finish_root)

    def finish_statechart():
      return statechart

    if ext_file is None:
      return ([("semantics?", parse_semantics), ("datamodel?", parse_datamodel), ("inport*", get_port_parser(statechart.in_events)), ("outport*", get_port_parser(statechart.out_events)), ("root", parse_root)], finish_statechart)
    else:
      return ([("override_semantics?", parse_semantics)], finish_statechart)

  return parse_statechart
