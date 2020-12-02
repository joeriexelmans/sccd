from typing import *
from sccd.statechart.static.tree import *
from sccd.util.visit_tree import *
from sccd.statechart.static.statechart import *
from sccd.statechart.static.globals import *
from sccd.util.indenting_writer import *

# Conversion functions from abstract syntax elements to identifiers in Rust

def snake_case(state: State) -> str:
    return state.opt.full_name.replace('/', '_');

def ident_var(state: State) -> str:
    if state.opt.full_name == "/":
        return "root" # no technical reason, it's just clearer than "s_"
    else:
        return "s" + snake_case(state)

def ident_type(state: State) -> str:
    if state.opt.full_name == "/":
        return "Root" # no technical reason, it's just clearer than "State_"
    else:
        return "State" + snake_case(state)

def ident_enum_variant(state: State) -> str:
    # We know the direct children of a state must have unique names relative to each other,
    # and enum variants are scoped locally, so we can use the short name here:
    return state.short_name

def ident_field(state: State) -> str:
    return "s" + snake_case(state)

def ident_source_target(state: State) -> str:
    # drop the first '_' (this is safe, the root state itself can never be source or target)
    return snake_case(state)[1:]

def ident_transition(t: Transition) -> str:
    return "transition%d_FROM_%s_TO_%s" % (t.opt.id, ident_source_target(t.source), ident_source_target(t.target))

def ident_arena_label(state: State) -> str:
    if state.opt.full_name == "/":
        return "arena_root"
    else:
        return "arena" + snake_case(state)

def ident_history_field(state: HistoryState) -> str:
    return "history" + snake_case(state.parent) # A history state records history value for its parent

# Name of the output callback parameter, everywhere
IDENT_OC = "_output" # underscore to keep Rust from warning us for unused variable

def compile_actions(actions: List[Action], w: IndentingWriter):
    for a in actions:
        if isinstance(a, RaiseOutputEvent):
            # TODO: evaluate event parameters
            w.writeln("%s(\"%s\", \"%s\");" % (IDENT_OC, a.outport, a.name))
        else:
            w.writeln("panic!(\"Unimplemented action %s (%s)\");" % (type(a), a.render()))

def compile_statechart(sc: Statechart, globals: Globals, w: IndentingWriter):

    # TODO: Do not create a StatechartInstance just to check if priorities are valid:
    from sccd.statechart.dynamic.statechart_instance import StatechartInstance
    StatechartInstance(sc, None, None, None, None) # may raise error if priorities are invalid

    tree = sc.tree

    # Note: The reason for the
    #    #[allow(non_camel_case_types)]
    # lines is that we cannot convert the casing of our state's names:
    # SCCD allows any combination of upper and lower case symbols, and
    # converting to, say, camelcase, as Rust likes it for type names,
    # could cause naming collisions.
    # (these naming collisions would be detected by the Rust compiler, so the error would not go unnoticed,
    # still, it's better to NOT break our model :)

    # Write 'current state' types

    def write_state_type(state: State, children: List[State]):
        if isinstance(state, HistoryState):
            return None # we got no time for pseudo-states!

        w.writeln("#[allow(non_camel_case_types)]")
        w.writeln("#[derive(Copy, Clone)]")

        def as_struct():
            w.writeln("struct %s {" % ident_type(state))
            for child in children:
                if child is not None:
                    w.writeln("  %s: %s," % (ident_field(child), ident_type(child)))
            w.writeln("}")

        def as_enum():
            w.writeln("enum %s {" % ident_type(state))
            for child in children:
                if child is not None:
                    w.writeln("  %s(%s)," % (ident_enum_variant(child), ident_type(child)))
            w.writeln("}")

        if isinstance(state, ParallelState):
            w.writeln("// And-state")
            as_struct()
        elif isinstance(state, State):
            if len(state.children) > 0:
                w.writeln("// Or-state")
                as_enum() # Or-state
            else:
                # Basic state: write as empty struct
                #
                # An empty struct in Rust is a type with one possible value.
                # An empty struct is a Zero-Sized Type.
                #
                # An empty enum is also a valid type in Rust, but no instances
                # of it can be created. Also called an "uninhabited type".
                w.writeln("// Basic state")
                as_struct()

            # The above if-else construction hints at the fact that we would have
            # better used empty And-states to model basic states, instead of empty Or-states...

        w.writeln()
        return state


    # Write "default" constructor

    def write_default(state: State, children: List[State]):
        if isinstance(state, HistoryState):
            return None # we got no time for pseudo-states!

        # We use Rust's Default-trait to record default states,
        # this way, constructing a state instance without parameters will initialize it as the default state.

        w.writeln("impl Default for %s {" % ident_type(state))
        w.writeln("  fn default() -> Self {")

        if isinstance(state, ParallelState):
            w.writeln("    Self {")
            for child in children:
                if child is not None:
                    w.writeln("      %s: Default::default()," % (ident_field(child)))
            w.writeln("    }")
        elif isinstance(state, State):
            if state.default_state is not None:
                # Or-state
                w.writeln("    Self::%s(Default::default())" % (ident_enum_variant(state.default_state)))
            else:
                # Basic state
                w.writeln("    Self{}")

        w.writeln("  }")
        w.writeln("}")
        w.writeln()
        return state

    # Write "enter/exit state" functions

    def write_enter_exit(state: State, children: List[State]):
        if isinstance(state, HistoryState):
            return None # we got no time for pseudo-states!

        w.writeln("impl<'a, OutputCallback: FnMut(&'a str, &'a str)> State<OutputCallback> for %s {" % ident_type(state))

        w.writeln("  fn enter_actions(%s: &mut OutputCallback) {" % IDENT_OC)
        w.writeln("    println!(\"enter %s\");" % state.opt.full_name);
        w.indent(); w.indent()
        compile_actions(state.enter, w)
        w.dedent(); w.dedent()
        w.writeln("  }")

        w.writeln("  fn exit_actions(%s: &mut OutputCallback) {" % IDENT_OC)
        w.writeln("    println!(\"exit %s\");" % state.opt.full_name);
        w.indent(); w.indent()
        compile_actions(state.exit, w)
        w.dedent(); w.dedent()
        w.writeln("  }")

        w.writeln("  fn enter_default(%s: &mut OutputCallback) {" % IDENT_OC)
        w.writeln("    %s::enter_actions(%s);" % (ident_type(state), IDENT_OC))
        if isinstance(state, ParallelState):
            for child in children:
                if child is not None:
                    w.writeln("    %s::enter_default(%s);" % (ident_type(child), IDENT_OC))
        else:
            if state.default_state is not None:
                w.writeln("    %s::enter_default(%s);" % (ident_type(state.default_state), IDENT_OC))
        w.writeln("  }")

        w.writeln("  fn exit_current(&self, %s: &mut OutputCallback) {" % IDENT_OC)
        # Children's exit actions
        if isinstance(state, ParallelState):
            for child in children:
                if child is not None:
                    w.writeln("    self.%s.exit_current(%s);" % (ident_field(child), IDENT_OC))
        else:
            if len(children) > 0:
                w.writeln("    match self {")
                for child in children:
                    if child is not None:
                        w.writeln("      Self::%s(s) => { s.exit_current(%s); }," % (ident_enum_variant(child), IDENT_OC))
                w.writeln("    }")
        # Our own exit actions
        w.writeln("    %s::exit_actions(%s);" % (ident_type(state), IDENT_OC))
        w.writeln("  }")

        w.writeln("  fn enter_current(&self, %s: &mut OutputCallback) {" % IDENT_OC)
        # Children's enter actions
        w.writeln("    %s::enter_actions(%s);" % (ident_type(state), IDENT_OC))
        # Our own enter actions
        if isinstance(state, ParallelState):
            for child in children:
                if child is not None:
                    w.writeln("    self.%s.enter_current(%s);" % (ident_field(child), IDENT_OC))
        else:
            if len(children) > 0:
                w.writeln("    match self {")
                for child in children:
                    if child is not None:
                        w.writeln("      Self::%s(s) => { s.enter_current(%s); }," % (ident_enum_variant(child), IDENT_OC))
                w.writeln("    }")
        w.writeln("  }")

        w.writeln("}")
        w.writeln()
        return state

    visit_tree(tree.root, lambda s: s.children,
        child_first=[
            write_state_type,
            write_default,
            write_enter_exit,
        ])

    # Write event type

    w.writeln("#[allow(non_camel_case_types)]")
    w.writeln("#[derive(Copy, Clone)]")
    w.writeln("enum Event {")
    for event_name in (globals.events.names[i] for i in bm_items(sc.internal_events)):
        w.writeln("  %s," % event_name)
    w.writeln("}")
    w.writeln()

    # Write statechart type
    w.writeln("pub struct Statechart {")
    w.writeln("  current_state: %s," % ident_type(tree.root))
    if len(tree.history_states) > 0:
        # w.writeln("  // History values")
        for h in tree.history_states:
            w.writeln("  %s: %s," % (ident_history_field(h), ident_type(h.parent)))
    w.writeln("  // TODO: timers")
    w.writeln("}")
    w.writeln()

    w.writeln("impl Default for Statechart {")
    w.writeln("  fn default() -> Self {")
    w.writeln("    Self {")
    w.writeln("      current_state: Default::default(),")
    for h in tree.history_states:
        w.writeln("      %s: Default::default()," % (ident_history_field(h)))
    # w.writeln("      timers: Default::default(),")
    w.writeln("    }")
    w.writeln("  }")
    w.writeln("}")
    w.writeln()

    w.writeln("impl<'a, OutputCallback: FnMut(&'a str, &'a str)> SC<Event, OutputCallback> for Statechart {")
    w.writeln("  fn init(%s: &mut OutputCallback) {" % IDENT_OC)
    w.writeln("    %s::enter_default(%s);" % (ident_type(tree.root), IDENT_OC))
    w.writeln("  }")
    w.writeln("  fn fair_step(&mut self, _event: Option<Event>, %s: &mut OutputCallback) -> bool {" % IDENT_OC)
    w.writeln("    #![allow(non_snake_case)]")
    w.writeln("    #![allow(unused_labels)]")
    w.writeln("    #![allow(unused_variables)]")
    w.writeln("    println!(\"fair step\");")
    w.writeln("    let mut fired = false;")
    w.writeln("    let %s = &mut self.current_state;" % ident_var(tree.root))

    w.indent()
    w.indent()

    def write_transitions(state: State):
        if isinstance(state, HistoryState):
            return None # we got no time for pseudo-states!

        # Many of the states to exit can be computed statically (i.e. they are always the same)
        # The one we cannot compute statically are:
        #
        # (1) The descendants of S2, S3, etc. if S1 is part of the "exit path":
        #
        #      A        ---> And-state on exit path
        #    / \   \
        #   S1  S2  S3 ...
        #
        #    |
        #    +--> S1 also on exit path
        #
        # (2) The descendants of S, if S is the transition target
        #
        # The same applies to entering states.

        # Writes statements that perform exit actions
        # in the correct order (children (last to first), then parent) for given 'exit path'.
        def write_exit(exit_path: List[State]):
            # w.writeln("println!(\"exit path = %s\");" % str(exit_path).replace('"', "'"))
            if len(exit_path) > 0:
                s = exit_path[0] # state to exit

                if len(exit_path) == 1:
                    # Exit s:
                    w.writeln("%s.exit_current(%s);" % (ident_var(s), IDENT_OC))
                else:
                    # Exit children:
                    if isinstance(s, ParallelState):
                        for c in reversed(s.children):
                            if exit_path[1] is c:
                                write_exit(exit_path[1:]) # continue recursively
                            else:
                                w.writeln("%s.exit_current(%s);" % (ident_var(c), IDENT_OC))
                    elif isinstance(s, State):
                        if s.default_state is not None:
                            # Or-state
                            write_exit(exit_path[1:]) # continue recursively with the next child on the exit path

                    # Exit s:
                    w.writeln("%s::exit_actions(%s);" % (ident_type(s), IDENT_OC))

                # Store history
                if s.opt.deep_history:
                    _, _, h = s.opt.deep_history
                    w.writeln("self.%s = *%s; // Store deep history" % (ident_history_field(h), ident_var(s)))
                if s.opt.shallow_history:
                    _, h = s.opt.shallow_history
                    if isinstance(s, ParallelState):
                        raise Exception("Shallow history makes no sense for And-state!")
                    w.writeln("self.%s = match %s { // Store shallow history" % (ident_history_field(h), ident_var(s)))
                    for c in s.children:
                        if not isinstance(c, HistoryState):
                            w.writeln("  %s::%s(_) => %s::%s(%s::default())," % (ident_type(s), ident_enum_variant(c), ident_type(s), ident_enum_variant(c), ident_type(c)))
                    w.writeln("};")
                    # w.writeln("println!(\"recorded history\");")

        # Writes statements that perform enter actions
        # in the correct order (parent, children (first to last)) for given 'enter path'.
        def write_enter(enter_path: List[State]):
            if len(enter_path) > 0:
                s = enter_path[0] # state to enter
                if len(enter_path) == 1:
                    # Target state.
                    if isinstance(s, HistoryState):
                        w.writeln("self.%s.enter_current(%s); // Enter actions for history state" %(ident_history_field(s), IDENT_OC))
                    else:
                        w.writeln("%s::enter_default(%s);" % (ident_type(s), IDENT_OC))
                else:
                    # Enter s:
                    w.writeln("%s::enter_actions(%s);" % (ident_type(s), IDENT_OC))
                    # Enter children:
                    if isinstance(s, ParallelState):
                        for c in s.children:
                            if enter_path[1] is c:
                                # if not isinstance(c, HistoryState):
                                #     w.writeln("%s::enter_actions(%s);" % (ident_type(c), IDENT_OC))
                                write_enter(enter_path[1:]) # continue recursively
                            else:
                                w.writeln("%s::enter_default(%s);" % (ident_type(c), IDENT_OC))
                    elif isinstance(s, State):
                        if len(s.children) > 0:
                            write_enter(enter_path[1:]) # continue recursively with the next child on the enter path
                        else:
                            # If the following occurs, there's a bug in this source file
                            raise Exception("Basic state in the middle of enter path")

        # The 'state' of a state is just a value in our compiled code.
        # When executing a transition, the value of the transition's arena changes.
        # This function writes statements that build a new value that can be assigned to the arena.
        def write_new_configuration(enter_path: List[State]):
            if len(enter_path) > 0:
                s = enter_path[0]
                if len(enter_path) == 1:
                    # Construct target state.
                    # And/Or/Basic state: Just construct the default value:
                    w.writeln("let new_%s: %s = Default::default();" % (ident_var(s), ident_type(s)))
                else:
                    next_child = enter_path[1]
                    if isinstance(next_child, HistoryState):
                        # No recursion
                        w.writeln("let new_%s = self.%s; // Restore history value" % (ident_var(s), ident_history_field(next_child)))
                    else:
                        if isinstance(s, ParallelState):
                            for c in s.children:
                                if next_child is c:
                                    write_new_configuration(enter_path[1:]) # recurse
                                else:
                                    # Other children's default states are constructed
                                    w.writeln("let new_%s: %s = Default::default();" % (ident_var(c), ident_type(c)))
                            # Construct struct
                            # if isinstance(next_child, HistoryState):
                            #     w.writeln("let new_%s = %s{%s:%s, ..Default::default()};" % (ident_var(s), ident_type(s), ident_field(next_child), ident_var(next_child)))
                            # else:
                            w.writeln("let new_%s = %s{%s:%s, ..Default::default()};" % (ident_var(s), ident_type(s), ident_field(next_child), ident_var(next_child)))
                        elif isinstance(s, State):
                            if len(s.children) > 0:
                                # Or-state
                                write_new_configuration(enter_path[1:]) # recurse
                                # Construct enum value
                                w.writeln("let new_%s = %s::%s(new_%s);" % (ident_var(s), ident_type(s), ident_enum_variant(next_child), ident_var(next_child)))
                            else:
                                # If the following occurs, there's a bug in this source file
                                raise Exception("Basic state in the middle of enter path")

        def parent():
            for i, t in enumerate(state.transitions):
                w.writeln("// Outgoing transition %d" % i)

                if t.trigger is not EMPTY_TRIGGER:
                    if len(t.trigger.enabling) > 1:
                        raise Exception("Multi-event triggers currently unsupported")
                    w.writeln("if let Some(Event::%s) = _event {" % t.trigger.enabling[0].name)
                    w.indent()

                # 1. Execute transition's actions

                # Path from arena to source, including source but not including arena
                exit_path_bm = t.opt.arena.opt.descendants & (t.source.opt.state_id_bitmap | t.source.opt.ancestors) # bitmap
                exit_path = list(tree.bitmap_to_states(exit_path_bm)) # list of states

                # Path from arena to target, including target but not including arena
                enter_path_bm = t.opt.arena.opt.descendants & (t.target.opt.state_id_bitmap | t.target.opt.ancestors) # bitmap
                enter_path = list(tree.bitmap_to_states(enter_path_bm)) # list of states

                w.writeln("println!(\"fire %s\");" % str(t))

                w.writeln("// Exit actions")
                write_exit(exit_path)

                if len(t.actions) > 0:
                    w.writeln("// Transition's actions")
                    compile_actions(t.actions, w)

                w.writeln("// Enter actions")
                write_enter(enter_path)

                # 2. Update state

                # A state configuration is just a value
                w.writeln("// Build new state configuration")
                write_new_configuration([t.opt.arena] + enter_path)

                w.writeln("// Update arena configuration")
                w.writeln("*%s = new_%s;" % (ident_var(t.opt.arena), ident_var(t.opt.arena)))

                w.writeln("fired = true;")

                # This arena is done:
                w.writeln("break '%s;" % (ident_arena_label(t.opt.arena)))

                if t.trigger is not EMPTY_TRIGGER:
                    w.dedent()
                    w.writeln("}")

        def child():
            # Here is were we recurse and write the transition code for the children of our 'state'.
            if isinstance(state, ParallelState):
                for child in state.children:
                    if not isinstance(child, HistoryState):
                        w.writeln("// Orthogonal region")
                        w.writeln("let %s = &mut %s.%s;" % (ident_var(child), ident_var(state), ident_field(child)))
                        write_transitions(child)
            elif isinstance(state, State):
                if state.default_state is not None:
                    w.writeln("'%s: loop {" % ident_arena_label(state))
                    w.indent()
                    w.writeln("match %s {" % ident_var(state))
                    for child in state.children:
                        if isinstance(child, HistoryState):
                            continue
                        w.indent()
                        w.writeln("%s::%s(%s) => {" % (ident_type(state), ident_enum_variant(child), ident_var(child)))
                        w.indent()
                        write_transitions(child)
                        w.dedent()
                        w.writeln("},")
                        w.dedent()
                    w.writeln("};")
                    w.writeln("break;")
                    w.dedent()
                    w.writeln("}")


        if sc.semantics.hierarchical_priority == HierarchicalPriority.SOURCE_PARENT:
            parent()
            child()
        elif sc.semantics.hierarchical_priority == HierarchicalPriority.SOURCE_CHILD:
            child()
            parent()
        elif sc.semantics.hierarchical_priority == HierarchicalPriority.NONE:
            # We're free to pick any semantics here, but let's not go too wild
            parent()
            child()
        else:
            raise Exception("Unsupported semantics %s" % sc.semantics.hierarchical_priority)

    write_transitions(tree.root)

    w.dedent()
    w.dedent()

    w.writeln("    fired")
    w.writeln("  }")

    def write_stepping_function(name: str, title: str, maximality: Maximality, substep: str, input_whole: bool):
        w.writeln("  fn %s(&mut self, event: Option<Event>, %s: &mut OutputCallback) -> bool {" % (name, IDENT_OC))
        w.writeln("    println!(\"%s\");" % name)
        if maximality == Maximality.TAKE_ONE:
            w.writeln("    // %s Maximality: Take One" % title)
            w.writeln("    self.fair_step(event, %s)" % IDENT_OC)
        elif maximality == Maximality.TAKE_MANY:
            w.writeln("    let mut fired = false;")
            w.writeln("    // %s Maximality: Take Many" % title)
            w.writeln("    let mut e = event;")
            w.writeln("    loop {")
            w.writeln("      let just_fired = self.%s(e, %s);" % (substep, IDENT_OC))
            w.writeln("      if !just_fired {")
            w.writeln("        break;")
            w.writeln("      }")
            w.writeln("      fired |= just_fired;")
            if not input_whole:
                w.writeln("      // Input Event Lifeline: %s" % sc.semantics.input_event_lifeline)
                w.writeln("      e = None;")
            w.writeln("    }")
            w.writeln("    fired")
        else:
            raise Exception("Unsupported semantics %s" % sc.semantics.big_step_maximality)
        w.writeln("  }")

    write_stepping_function("combo_step", "Combo-Step", sc.semantics.combo_step_maximality, substep="fair_step", input_whole = sc.semantics.input_event_lifeline == InputEventLifeline.WHOLE or
                sc.semantics.input_event_lifeline == InputEventLifeline.FIRST_COMBO_STEP)
    write_stepping_function("big_step", "Big-Step", sc.semantics.big_step_maximality, substep="combo_step",
        input_whole = sc.semantics.input_event_lifeline == InputEventLifeline.WHOLE)

    # w.writeln("  fn combo_step(&mut self, event: Option<Event>, %s: &mut OutputCallback) {" % IDENT_OC)
    # w.writeln("    ")
    # w.writeln("  }")


    w.writeln("}")
    w.writeln()
