from sccd.statechart.parser.xml import *
from sccd.statechart.dynamic.statechart_instance import *

if __name__ == "__main__":
  
  # Load model
  globals = Globals()
  rules = statechart_parser_rules(globals, path=".")
  statechart_model = parse_f("statechart_semantics.xml", [("statechart", rules)])
  globals.init_durations()


  # Generate semantic variants, and filter invalid ones
  variants = statechart_model.generate_semantic_variants()

  def is_valid(semantics):
    if semantics.combo_step_maximality > semantics.big_step_maximality:
      return False

    if semantics.assignment_memory_protocol != semantics.enabledness_memory_protocol:
      return False

    must_have_combo_steps = (semantics.input_event_lifeline == InputEventLifeline.FIRST_COMBO_STEP or
          semantics.internal_event_lifeline == InternalEventLifeline.NEXT_COMBO_STEP or
          semantics.enabledness_memory_protocol == MemoryProtocol.COMBO_STEP)

    if not must_have_combo_steps and semantics.combo_step_maximality > Maximality.TAKE_ONE:
      return False

    if semantics.big_step_maximality == Maximality.TAKE_ONE and must_have_combo_steps:
      return False

    return True

  valid_variants = [v for v in variants if is_valid(v.semantics)]

  print("Total variants:", len(variants))
  print("Valid variants:", len(valid_variants))


  # We'll need these mappings to translate the statechart's post-big-step configuration to a semantic configuration
  state_name_to_semantics = {
    "/P/BigStepMaximality/TakeOne": ("big_step_maximality", Maximality.TAKE_ONE),
    "/P/BigStepMaximality/Syntactic": ("big_step_maximality", Maximality.SYNTACTIC),
    "/P/BigStepMaximality/TakeMany": ("big_step_maximality", Maximality.TAKE_MANY),

    "/P/ComboStepMaximality/ComboStepMaximality/TakeOne": ("combo_step_maximality", Maximality.TAKE_ONE),
    "/P/ComboStepMaximality/ComboStepMaximality/Syntactic": ("combo_step_maximality", Maximality.SYNTACTIC),
    "/P/ComboStepMaximality/ComboStepMaximality/TakeMany": ("combo_step_maximality", Maximality.TAKE_MANY),

    "/P/InputEventLifeline/FirstSmallStep": ("input_event_lifeline", InputEventLifeline.FIRST_SMALL_STEP),
    "/P/InputEventLifeline/FirstComboStep": ("input_event_lifeline", InputEventLifeline.FIRST_COMBO_STEP),
    "/P/InputEventLifeline/Whole": ("input_event_lifeline", InputEventLifeline.WHOLE),

    "/P/InternalEventLifeline/InternalEventLifeline/NextSmallStep": ("internal_event_lifeline", InternalEventLifeline.NEXT_SMALL_STEP),
    "/P/InternalEventLifeline/InternalEventLifeline/NextComboStep": ("internal_event_lifeline", InternalEventLifeline.NEXT_COMBO_STEP),
    "/P/InternalEventLifeline/InternalEventLifeline/Remainder": ("internal_event_lifeline", InternalEventLifeline.REMAINDER),
    "/P/InternalEventLifeline/InternalEventLifeline/Queue": ("internal_event_lifeline", InternalEventLifeline.QUEUE),

    "/P/MemoryProtocol/MemoryProtocol/BigStep": ("enabledness_memory_protocol", MemoryProtocol.BIG_STEP),
    "/P/MemoryProtocol/MemoryProtocol/ComboStep": ("enabledness_memory_protocol", MemoryProtocol.COMBO_STEP),
    "/P/MemoryProtocol/MemoryProtocol/SmallStep": ("enabledness_memory_protocol", MemoryProtocol.SMALL_STEP),

    "/P/Priority/SourceParent": ("priority", Priority.SOURCE_PARENT),
    "/P/Priority/SourceChild": ("priority", Priority.SOURCE_CHILD),
  }

  state_id_to_semantics = {
    statechart_model.tree.state_dict[state_name].opt.state_id: tup
      for state_name, tup in state_name_to_semantics.items()
  }


  # Some mock callbacks that we have pass to the StatechartInstance
  def on_output(e: OutputEvent):
    pass

  def schedule(after, event, targets):
    return 0

  def cancel(id):
    pass

  # List of input events for the big-step is always the same, so declare it outside the loop
  input0_id = globals.events.get_id("input0")
  input_events = [InternalEvent(id=input0_id, name="", params=[])]

  # Here we will accumulate our wrongly-inferred semantic configurations
  incorrect = []

  for v in valid_variants:
    instance = StatechartInstance(
      statechart=v,
      object_manager=None,
      output_callback=on_output,
      schedule_callback=schedule,
      cancel_callback=cancel)

    instance.initialize()
    instance.big_step(input_events)

    inferred_semantics = SemanticConfiguration()
    for state_id in bm_items(instance.execution.configuration):
      if state_id in state_id_to_semantics:
        aspect_name, aspect_val = state_id_to_semantics[state_id]
        setattr(inferred_semantics, aspect_name, aspect_val)
    inferred_semantics.assignment_memory_protocol = inferred_semantics.enabledness_memory_protocol

    # print("\nActual semantics:")
    # print(v.semantics)

    # print("\nInferred semantics:")
    # print(inferred_semantics)

    if v.semantics != inferred_semantics:
      incorrect.append((v.semantics, inferred_semantics))

  if len(incorrect) > 0:
    for actual, inferred in incorrect:
      print("Actual semantics:")
      print(actual)

      print("Inferred semantics:")
      print(inferred)
    print("Did not correctly infer semantics for %d variants." % len(incorrect))
  else:
    print("Correctly inferred semantics for all semantic configurations!")
