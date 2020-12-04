from typing import *
from sccd.statechart.static.tree import *
from sccd.util.visit_tree import *
from sccd.statechart.static.statechart import *
from sccd.statechart.static.globals import *
from sccd.util.indenting_writer import *

class UnsupportedFeature(Exception):
    pass

# Conversion functions from abstract syntax elements to identifiers in Rust

def snake_case(state: State) -> str:
    return state.full_name.replace('/', '_');

def ident_var(state: State) -> str:
    if state.full_name == "/":
        return "root" # no technical reason, it's just clearer than "s_"
    else:
        return "s" + snake_case(state)

def ident_type(state: State) -> str:
    if state.full_name == "/":
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
    return "transition%d_FROM_%s_TO_%s" % (t.id, ident_source_target(t.source), ident_source_target(t.target))

def ident_arena_label(state: State) -> str:
    if state.full_name == "/":
        return "arena_root"
    else:
        return "arena" + snake_case(state)

def ident_arena_const(state: State) -> str:
    if state.full_name == "/":
        return "ARENA_ROOT"
    else:
        return "ARENA" + snake_case(state)

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
            raise UnsupportedFeature(str(type(a)))

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
        w.writeln("#[allow(non_camel_case_types)]")
        w.writeln("#[derive(Copy, Clone)]")

        def as_struct():
            w.writeln("struct %s {" % ident_type(state))
            for child in children:
                w.writeln("  %s: %s," % (ident_field(child), ident_type(child)))
            w.writeln("}")

        def as_enum():
            w.writeln("enum %s {" % ident_type(state))
            for child in children:
                w.writeln("  %s(%s)," % (ident_enum_variant(child), ident_type(child)))
            w.writeln("}")

        if isinstance(state.type, AndState):
            w.writeln("// And-state")
            as_struct()
        elif isinstance(state.type, OrState):
            w.writeln("// Or-state")
            as_enum()

        w.writeln()
        return state


    # Write "default" constructor

    def write_default(state: State, children: List[State]):
        # We use Rust's Default-trait to record default states,
        # this way, constructing a state instance without parameters will initialize it as the default state.

        w.writeln("impl Default for %s {" % ident_type(state))
        w.writeln("  fn default() -> Self {")

        if isinstance(state.type, AndState):
            w.writeln("    Self {")
            for child in children:
                w.writeln("      %s: Default::default()," % (ident_field(child)))
            w.writeln("    }")
        elif isinstance(state.type, OrState):
            w.writeln("    Self::%s(Default::default())" % (ident_enum_variant(state.type.default_state)))

        w.writeln("  }")
        w.writeln("}")
        w.writeln()
        return state

    # Write "enter/exit state" functions

    def write_enter_exit(state: State, children: List[State]):
        w.writeln("impl<'a, OutputCallback: FnMut(&'a str, &'a str)> State<OutputCallback> for %s {" % ident_type(state))

        w.writeln("  fn enter_actions(%s: &mut OutputCallback) {" % IDENT_OC)
        w.writeln("    println!(\"enter %s\");" % state.full_name);
        w.indent(); w.indent()
        compile_actions(state.enter, w)
        w.dedent(); w.dedent()
        w.writeln("  }")

        w.writeln("  fn exit_actions(%s: &mut OutputCallback) {" % IDENT_OC)
        w.writeln("    println!(\"exit %s\");" % state.full_name);
        w.indent(); w.indent()
        compile_actions(state.exit, w)
        w.dedent(); w.dedent()
        w.writeln("  }")

        w.writeln("  fn enter_default(%s: &mut OutputCallback) {" % IDENT_OC)
        w.writeln("    %s::enter_actions(%s);" % (ident_type(state), IDENT_OC))
        if isinstance(state.type, AndState):
            for child in children:
                w.writeln("    %s::enter_default(%s);" % (ident_type(child), IDENT_OC))
        elif isinstance(state.type, OrState):
            w.writeln("    %s::enter_default(%s);" % (ident_type(state.type.default_state), IDENT_OC))
        w.writeln("  }")

        w.writeln("  fn exit_current(&self, %s: &mut OutputCallback) {" % IDENT_OC)
        # Children's exit actions
        if isinstance(state.type, AndState):
            for child in children:
                w.writeln("    self.%s.exit_current(%s);" % (ident_field(child), IDENT_OC))
        elif isinstance(state.type, OrState):
            w.writeln("    match self {")
            for child in children:
                w.writeln("      Self::%s(s) => { s.exit_current(%s); }," % (ident_enum_variant(child), IDENT_OC))
            w.writeln("    }")
        # Our own exit actions
        w.writeln("    %s::exit_actions(%s);" % (ident_type(state), IDENT_OC))
        w.writeln("  }")

        w.writeln("  fn enter_current(&self, %s: &mut OutputCallback) {" % IDENT_OC)
        # Children's enter actions
        w.writeln("    %s::enter_actions(%s);" % (ident_type(state), IDENT_OC))
        # Our own enter actions
        if isinstance(state.type, AndState):
            for child in children:
                w.writeln("    self.%s.enter_current(%s);" % (ident_field(child), IDENT_OC))
        elif isinstance(state.type, OrState):
            w.writeln("    match self {")
            for child in children:
                w.writeln("      Self::%s(s) => { s.enter_current(%s); }," % (ident_enum_variant(child), IDENT_OC))
            w.writeln("    }")
        w.writeln("  }")

        w.writeln("}")
        w.writeln()
        return state

    visit_tree(tree.root, lambda s: s.real_children,
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

    # Write arena type
    arenas = set()
    for t in tree.transition_list:
        arenas.add(t.arena)
    w.writeln("// Arenas (bitmap type)")
    for size, typ in [(8, 'u8'), (16, 'u16'), (32, 'u32'), (64, 'u64'), (128, 'u128')]:
        if len(arenas) + 1 <= size:
            w.writeln("type Arenas = %s;" % typ)
            break
    else:
        raise Exception("Too many arenas! Cannot fit into an unsigned int.")
    for i, a in enumerate(arenas):
        w.writeln("const %s: Arenas = %d;" % (ident_arena_const(a), 2**i))
    # Just an extra bit to indicate that a transition has fired during fair_step
    # This is to decide when to stop stepping in case of Take Many or Take Syntactic
    w.writeln("const ARENA_FIRED: Arenas = %d;" % 2**(i+1))
    w.writeln()

    # Write statechart type
    w.writeln("pub struct Statechart {")
    w.writeln("  current_state: %s," % ident_type(tree.root))
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


    # Function fair_step: a single "Take One" Maximality 'round' (= nonoverlapping arenas allowed to fire 1 transition)
    w.writeln("fn fair_step<'a, OutputCallback: FnMut(&'a str, &'a str)>(sc: &mut Statechart, _event: Option<Event>, %s: &mut OutputCallback, dirty: Arenas) -> Arenas {" % IDENT_OC)
    w.writeln("  #![allow(non_snake_case)]")
    w.writeln("  #![allow(unused_labels)]")
    w.writeln("  #![allow(unused_variables)]")
    w.writeln("  println!(\"fair step, dirty={}\", dirty);")
    w.writeln("  let mut fired: Arenas = 0;")
    w.writeln("  let %s = &mut sc.current_state;" % ident_var(tree.root))
    w.indent()

    syntactic_maximality = (
        sc.semantics.big_step_maximality == Maximality.SYNTACTIC
        or sc.semantics.combo_step_maximality == Maximality.SYNTACTIC)


    def write_transitions(state: State):

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
                    if isinstance(s.type, AndState):
                        for c in reversed(s.children):
                            if exit_path[1] is c:
                                write_exit(exit_path[1:]) # continue recursively
                            else:
                                w.writeln("%s.exit_current(%s);" % (ident_var(c), IDENT_OC))
                    elif isinstance(s.type, OrState):
                        write_exit(exit_path[1:]) # continue recursively with the next child on the exit path

                    # Exit s:
                    w.writeln("%s::exit_actions(%s);" % (ident_type(s), IDENT_OC))

                # Store history
                if s.deep_history:
                    _, _, h = s.deep_history
                    w.writeln("sc.%s = *%s; // Store deep history" % (ident_history_field(h), ident_var(s)))
                if s.shallow_history:
                    _, h = s.shallow_history
                    if isinstance(s.type, AndState):
                        raise Exception("Shallow history makes no sense for And-state!")
                    # Or-state:
                    w.writeln("sc.%s = match %s { // Store shallow history" % (ident_history_field(h), ident_var(s)))
                    for c in s.real_children:
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
                        w.writeln("sc.%s.enter_current(%s); // Enter actions for history state" %(ident_history_field(s), IDENT_OC))
                    else:
                        w.writeln("%s::enter_default(%s);" % (ident_type(s), IDENT_OC))
                else:
                    # Enter s:
                    w.writeln("%s::enter_actions(%s);" % (ident_type(s), IDENT_OC))
                    # Enter children:
                    if isinstance(s.type, AndState):
                        for c in s.children:
                            if enter_path[1] is c:
                                write_enter(enter_path[1:]) # continue recursively
                            else:
                                w.writeln("%s::enter_default(%s);" % (ident_type(c), IDENT_OC))
                    elif isinstance(s.type, OrState):
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
                        w.writeln("let new_%s = sc.%s; // Restore history value" % (ident_var(s), ident_history_field(next_child)))
                    else:
                        if isinstance(s.type, AndState):
                            for c in s.children:
                                if next_child is c:
                                    write_new_configuration(enter_path[1:]) # recurse
                                else:
                                    # Other children's default states are constructed
                                    w.writeln("let new_%s: %s = Default::default();" % (ident_var(c), ident_type(c)))
                            # Construct struct
                            w.writeln("let new_%s = %s{%s:new_%s, ..Default::default()};" % (ident_var(s), ident_type(s), ident_field(next_child), ident_var(next_child)))
                        elif isinstance(s.type, OrState):
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
                        raise UnsupportedFeature("Multi-event trigger")
                    w.writeln("if let Some(Event::%s) = _event {" % t.trigger.enabling[0].name)
                    w.indent()

                if t.guard is not None:
                    raise UnsupportedFeature("Guard conditions currently unsupported")

                # 1. Execute transition's actions

                # Path from arena to source, including source but not including arena
                exit_path_bm = t.arena.descendants & (t.source.state_id_bitmap | t.source.ancestors) # bitmap
                exit_path = list(tree.bitmap_to_states(exit_path_bm)) # list of states

                # Path from arena to target, including target but not including arena
                enter_path_bm = t.arena.descendants & (t.target.state_id_bitmap | t.target.ancestors) # bitmap
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
                write_new_configuration([t.arena] + enter_path)

                w.writeln("// Update arena configuration")
                w.writeln("*%s = new_%s;" % (ident_var(t.arena), ident_var(t.arena)))

                if not syntactic_maximality or t.target.stable:
                    w.writeln("fired |= %s; // Stable target" % ident_arena_const(t.arena))
                else:
                    w.writeln("fired |= ARENA_FIRED; // Unstable target")

                # This arena is done:
                w.writeln("break '%s;" % (ident_arena_label(t.arena)))

                if t.trigger is not EMPTY_TRIGGER:
                    w.dedent()
                    w.writeln("}")

        def child():
            # Here is were we recurse and write the transition code for the children of our 'state'.
            if isinstance(state.type, AndState):
                for child in state.real_children:
                    w.writeln("// Orthogonal region")
                    w.writeln("let %s = &mut %s.%s;" % (ident_var(child), ident_var(state), ident_field(child)))
                    write_transitions(child)
            elif isinstance(state.type, OrState):
                if state.type.default_state is not None:
                    if syntactic_maximality and state in arenas:
                        w.writeln("if dirty & %s == 0 {" % ident_arena_const(state))
                        w.indent()

                    w.writeln("'%s: loop {" % ident_arena_label(state))
                    w.indent()
                    w.writeln("match %s {" % ident_var(state))
                    for child in state.real_children:
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

                    if syntactic_maximality and state in arenas:
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
            raise UnsupportedFeature("Priority semantics %s" % sc.semantics.hierarchical_priority)

    write_transitions(tree.root)

    w.dedent()

    w.writeln("  println!(\"end fair step, fired={}\", fired);")
    w.writeln("  fired")
    w.writeln("}")

    def write_stepping_function(name: str, title: str, maximality: Maximality, substep: str, input_whole: bool):
        w.write("fn %s<'a, OutputCallback: FnMut(&'a str, &'a str)>(sc: &mut Statechart, event: Option<Event>, %s: &mut OutputCallback, dirty: Arenas)" % (name, IDENT_OC))
        # if return_arenas:
        w.writeln(" -> Arenas {")
        # else:
            # w.writeln(" {")
        w.writeln("  println!(\"%s, dirty={}\", dirty);" % name)
        if maximality == Maximality.TAKE_ONE:
            w.writeln("  // %s Maximality: Take One" % title)
            # if return_arenas:
            w.writeln("  %s(sc, event, %s, dirty)" % (substep, IDENT_OC))
            # else:
            #     w.writeln("  %s(sc, event, %s);" % (substep, IDENT_OC))
        else:
            # if return_arenas:
            w.writeln("  let mut fired: Arenas = dirty;")
            w.writeln("  let mut e = event;")
            w.writeln("  loop {")
            if maximality == Maximality.TAKE_MANY:
                w.writeln("    // %s Maximality: Take Many" % title)
                w.writeln("    let just_fired = %s(sc, e, %s, 0);" % (substep, IDENT_OC))
            elif maximality == Maximality.SYNTACTIC:
                w.writeln("    // %s Maximality: Syntactic" % title)
                w.writeln("    let just_fired = %s(sc, e, %s, fired);" % (substep, IDENT_OC))
            w.writeln("    if just_fired == 0 {")
            w.writeln("      break;")
            w.writeln("    }")
            # if return_arenas:
            w.writeln("    fired |= just_fired & !ARENA_FIRED;")
            if not input_whole:
                w.writeln("    // Input Event Lifeline: %s" % sc.semantics.input_event_lifeline)
                w.writeln("    e = None;")
            w.writeln("  }")
            # if return_arenas:
            w.writeln("  println!(\"end %s, fired={}\", fired);" % name)
            w.writeln("  fired")
        w.writeln("}")

    write_stepping_function("combo_step", "Combo-Step",
        maximality=sc.semantics.combo_step_maximality,
        substep="fair_step",
        input_whole = sc.semantics.input_event_lifeline == InputEventLifeline.WHOLE or
                sc.semantics.input_event_lifeline == InputEventLifeline.FIRST_COMBO_STEP)

    write_stepping_function("big_step", "Big-Step",
        maximality=sc.semantics.big_step_maximality,
        substep="combo_step",
        input_whole = sc.semantics.input_event_lifeline == InputEventLifeline.WHOLE)

    w.writeln()

    # Implement 'SC' trait
    w.writeln("impl<'a, OutputCallback: FnMut(&'a str, &'a str)> SC<Event, OutputCallback> for Statechart {")
    w.writeln("  fn init(%s: &mut OutputCallback) {" % IDENT_OC)
    w.writeln("    %s::enter_default(%s)" % (ident_type(tree.root), IDENT_OC))
    w.writeln("  }")
    w.writeln("  fn big_step(&mut self, event: Option<Event>, output: &mut OutputCallback) {")
    w.writeln("    big_step(self, event, output, 0);")
    w.writeln("  }")
    w.writeln("}")
    w.writeln()

    if DEBUG:
        w.writeln("use std::mem::size_of;")
        w.writeln("fn debug_print_sizes() {")
        w.writeln("  println!(\"------------------------\");")
        w.writeln("  println!(\"info: Statechart: {} bytes\", size_of::<Statechart>());")
        w.writeln("  println!(\"info: Event: {} bytes\", size_of::<Event>());")
        w.writeln("  println!(\"info: Arenas: {} bytes\", size_of::<Arenas>());")
        def write_state_size(state):
            w.writeln("  println!(\"info: %s: {} bytes\", size_of::<%s>());" % (state.full_name, ident_type(state)))
            for child in state.real_children:
                write_state_size(child)
        write_state_size(tree.root)
        w.writeln("  println!(\"------------------------\");")
        w.writeln("}")
