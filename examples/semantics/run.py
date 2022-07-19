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

  variants_filtered = [v for v in variants if v.semantics.enabledness_memory_protocol == v.semantics.assignment_memory_protocol]

  print("Total variants:", len(variants_filtered))
  
  # These rules perfectly partition the set of variants into "valid" and "invalid":
  def is_valid(semantics):
    # Combo-steps should be smaller (or equal to) big-steps, obviously.
    if semantics.combo_step_maximality > semantics.big_step_maximality:
      return False

    # Combo steps only make sense if another semantic option refers to them
    combo_steps_defined = (semantics.input_event_lifeline == InputEventLifeline.FIRST_COMBO_STEP or
          semantics.internal_event_lifeline == InternalEventLifeline.NEXT_COMBO_STEP or
          semantics.enabledness_memory_protocol == MemoryProtocol.COMBO_STEP)

    if combo_steps_defined:
      if semantics.big_step_maximality == Maximality.TAKE_ONE:
        # Combo steps will always equal big steps, and therefore don't really exist!
        # E.g. Input event lifeline "Present in First Combo Step" should be "Present in Whole" instead.
        # E.g. Internal event lifeline "Present in Next Combo Step" makes no sense, the event will never be sensed!
        # E.g. Memory protocol "Combo Step" should be "Big Step" instead.
        return False
    else:
      # Has no effect
      if semantics.combo_step_maximality > Maximality.TAKE_ONE:
        return False

    return True

  valid_variants = [v for v in variants_filtered if is_valid(v.semantics)]
  invalid_variants = [v for v in variants_filtered if not is_valid(v.semantics)]

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

    "/P/Priority/SourceParent": ("hierarchical_priority", HierarchicalPriority.SOURCE_PARENT),
    "/P/Priority/SourceChild": ("hierarchical_priority", HierarchicalPriority.SOURCE_CHILD),
  }

  state_id_to_semantics = {
    statechart_model.tree.state_dict[state_name].state_id: tup
      for state_name, tup in state_name_to_semantics.items()
  }


  # Some mock callbacks that we have to pass to the StatechartInstance
  def on_output(e: OutputEvent):
    pass

  def schedule(after, event, targets):
    return 0

  def cancel(id):
    pass

  # List of input events for the big-step is always the same, so declare it outside the loop
  input_events = [InternalEvent(name="input0", params=[])]


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
  # for inc in correct:
  #   print("CORRECT:")
  #   print(inc)
  # for inc in incorrect:
  #   print("INCORRECT:")
  #   print("what it was:", inc[0])
  #   print("what the SC says it is:", inc[1])
  print("\nOf the valid variants, correctly inferred %d, incorrectly inferred %d." % (len(correct), len(incorrect)))
  correct, incorrect = check_variants(invalid_variants)
  print("Of the invalid variants, correctly inferred %d, incorrectly inferred %d." % (len(correct), len(incorrect)))
  # for inc in correct:
  #   print("CORRECT:")
  #   print(inc)
  # for inc in incorrect:
  #   print("INCORRECT:")
  #   print("what it was:", inc[0])
  #   print("what the SC says it is:", inc[1])

