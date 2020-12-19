from sccd.test.static.syntax import *

_empty_scope = Scope("test", parent=None)


def test_parser_rules(statechart_parser_rules):
  globals = Globals()
  input = []
  output = []

  def parse_test(el):
    def parse_input(el):

      def param_parser_rules():
        params = []
        def parse_param(el):
          text = require_attribute(el, "expr")
          expr = parse_expression(globals, text)
          expr.init_expr(scope=_empty_scope)
          params.append(expr.eval(memory=None))
        return (params, parse_param)

      def parse_time(time: str) -> Expression:
        expr = parse_expression(globals, time)
        type = expr.init_expr(scope=_empty_scope)
        check_duration_type(type)
        return expr

      def make_input_event(name: str, params):
        event_id = globals.events.get_id(name)
        return InternalEvent(id=event_id, name=name, params=params)

      def parse_input_event(el):
        # port = require_attribute(el, "port")
        name = require_attribute(el, "name")
        time = require_attribute(el, "time")
        time_expr = parse_time(time)
        params, params_parser = param_parser_rules()
        input.append(TestInputBag(
          events=[make_input_event(name, params)],
          timestamp=time_expr))
        return {"param": params_parser}

      def parse_bag(el):
        # bag of (simultaneous) input events
        time = require_attribute(el, "time")
        time_expr = parse_time(time)
        events = []
        input.append(TestInputBag(events, time_expr))
        def parse_bag_event(el):
          # port = require_attribute(el, "port")
          name = require_attribute(el, "name")
          params, params_parser = param_parser_rules()
          events.append(make_input_event(name, params))
          return {"param": params_parser}
        return {"event": parse_bag_event}

      return {"event": parse_input_event, "bag": parse_bag}

    def parse_output(el):
      def parse_big_step(el):
        big_step = []
        output.append(big_step)

        def parse_output_event(el):
          name = require_attribute(el, "name")
          port = require_attribute(el, "port")
          params = []
          big_step.append(OutputEvent(name=name, port=port, params=params))

          def parse_param(el):
            val_text = require_attribute(el, "val")
            val_expr = parse_expression(globals, val_text)
            val_expr.init_expr(scope=_empty_scope)
            val = val_expr.eval(memory=None)
            params.append(val)

          return [("param*", parse_param)]

        return [("event+", parse_output_event)]

      return [("big_step+", parse_big_step)]

    def finish_test(statechart):
      globals.init_durations(delta=None)
      variants = statechart.generate_semantic_variants()

      def variant_description(i, variant) -> str:
        if not variant:
          return ""
        text = "Semantic variant %d of %d:" % (i+1, len(variants))
        text += str(variant)
        return text

      return Test(variants=[TestVariant(
        name=variant_description(i, variant.semantics),
        cd=SingleInstanceCD(globals=globals, statechart=variant),
        input=input,
        output=output)
      for i, variant in enumerate(variants)])

    sc_rules = statechart_parser_rules(globals)
    return ([("statechart", sc_rules), ("input?", parse_input), ("output?", parse_output)], finish_test)

  return parse_test