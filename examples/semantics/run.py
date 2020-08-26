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

  print("Total variants:", len(variants))
  
  def is_valid(semantics):
    # Combo-steps should be smaller (or equal to) big-steps, obviously.
    if semantics.combo_step_maximality > semantics.big_step_maximality:
      return False

    # I cannot think of a reason why someone would ever set assignment memory protocol to a different value from enabledness memory protocol.
    # The model currently only detects enabledness memory protocol, anyway.
    if semantics.assignment_memory_protocol != semantics.enabledness_memory_protocol:
      return False

    # Combo steps only make sense if another semantic option refers to them
    must_have_combo_steps = (semantics.input_event_lifeline == InputEventLifeline.FIRST_COMBO_STEP or
          semantics.internal_event_lifeline == InternalEventLifeline.NEXT_COMBO_STEP or
          semantics.enabledness_memory_protocol == MemoryProtocol.COMBO_STEP)

    # "Combo Take One" is the default combo-step maximality option in SCCD, and is also the option
    # that is chosen when no combo-steps are being defined. Options different from "Combo Take One"
    # are only allowed when combo-step semantics are being used.
    if not must_have_combo_steps and semantics.combo_step_maximality > Maximality.TAKE_ONE:
      return False

    # If big-step maximality is "Take One", a big-step will always equal a combo step. 
    # Therefore combo-steps do not really exist as entities that should be referred to by other semantic options.
    # E.g. Input event lifeline "Present in First Combo Step" should be "Present in Whole" instead.
    # E.g. Internal event lifeline "Present in Next Combo Step" makes no sense, the event will never be sensed!
    # E.g. Memory protocol "Combo Step" should be "Big Step" instead.
    if semantics.big_step_maximality == Maximality.TAKE_ONE and must_have_combo_steps:
      return False

    return True

  valid_variants = [v for v in variants if is_valid(v.semantics)]
  invalid_variants = [v for v in variants if not is_valid(v.semantics)]

  print("Valid variants:", len(valid_variants))
  print("Invalid variants:", len(invalid_variants))


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

    "/P/Priority/SourceParent": ("priority", HierarchicalPriority.SOURCE_PARENT),
    "/P/Priority/SourceChild": ("priority", HierarchicalPriority.SOURCE_CHILD),
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
  def check_variants(variants):
    correct = []
    incorrect = []

    for v in variants:
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

      if v.semantics == inferred_semantics:
        correct.append(inferred_semantics)
      else:
        incorrect.append((v.semantics, inferred_semantics))

    return (correct, incorrect)

  correct, incorrect = check_variants(valid_variants)
  print("\nOf the valid variants, corrently inferred %d, incorrectly inferred %d." % (len(correct), len(incorrect)))
  correct, incorrect = check_variants(invalid_variants)
  print("Of the invalid variants, corrently inferred %d, incorrectly inferred %d." % (len(correct), len(incorrect)))
