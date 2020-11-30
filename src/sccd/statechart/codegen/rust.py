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


def compile_statechart(sc: Statechart, globals: Globals, w: IndentingWriter):

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

        def as_struct():
            w.writeln("#[allow(non_camel_case_types)]")
            w.writeln("struct %s {" % ident_type(state))
            for child in children:
                w.writeln("  %s: %s," % (ident_field(child), ident_type(child)))
            w.writeln("}")

        def as_enum():
            w.writeln("#[allow(non_camel_case_types)]")
            w.writeln("enum %s {" % ident_type(state))
            for child in children:
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


    # Write "enter/exit state" functions

    # This fragment should be moved to a library:
    w.writeln("pub trait State {")
    w.writeln("  fn enter_actions();")
    w.writeln("  fn exit_actions();")
    w.writeln("  fn enter_default();")
    w.writeln("}")
    w.writeln()

    def write_enter_exit(state: State, children: List[State]):
        if isinstance(state, HistoryState):
            return None # we got no time for pseudo-states!

        w.writeln("impl State for %s {" % ident_type(state))

        w.writeln("  fn enter_actions() {")
        w.writeln("    println!(\"enter %s\");" % state.opt.full_name);
        for a in state.enter:
            w.writeln("    println!(\"%s\");" % a.render())
        w.writeln("  }")

        w.writeln("  fn exit_actions() {")
        w.writeln("    println!(\"exit %s\");" % state.opt.full_name);
        for a in state.exit:
            w.writeln("    println!(\"%s\");" % a.render())
        w.writeln("  }")

        w.writeln("  fn enter_default() {")
        w.writeln("    %s::enter_actions();" % ident_type(state))
        if isinstance(state, ParallelState):
            for child in children:
                w.writeln("    %s::enter_default();" % ident_type(child))
        else:
            if state.default_state is not None:
                w.writeln("    %s::enter_default();" % ident_type(state.default_state))
        w.writeln("  }")

        w.writeln("}")
        w.writeln()
        return state


    # Write "enter default state" functions

    def write_enter_default(state: State, children: List[State]):
        if isinstance(state, HistoryState):
            return None # we got no time for pseudo-states!

        # We use Rust's Default-trait to record default states,
        # this way, constructing a state instance without parameters will initialize it as the default state.

        w.writeln("impl Default for %s {" % ident_type(state))
        w.writeln("  fn default() -> Self {")

        if isinstance(state, ParallelState):
            w.writeln("    return Self {")
            for child in children:
                w.writeln("      %s: Default::default()," % (ident_field(child)))
            w.writeln("    };")
        elif isinstance(state, State):
            if state.default_state is not None:
                # Or-state
                w.writeln("    return Self::%s(Default::default());" % (ident_enum_variant(state.default_state)))
            else:
                # Basic state
                w.writeln("    return Self{};")

        w.writeln("  }")
        w.writeln("}")
        w.writeln()
        return state

    visit_tree(tree.root, lambda s: s.children,
        child_first=[
            write_state_type,
            write_enter_exit,
            write_enter_default,
        ])

    # Write event type

    w.writeln("#[allow(non_camel_case_types)]")
    w.writeln("enum Event {")
    for event_name in (globals.events.names[i] for i in bm_items(sc.internal_events)):
        w.writeln("  %s," % event_name)
    w.writeln("}")
    w.writeln()

    # Write statechart type
    w.writeln("pub struct Statechart {")
    w.writeln("  current_state: %s," % ident_type(tree.root))
    w.writeln("  // TODO: history values")
    w.writeln("  // TODO: timers")
    w.writeln("}")
    w.writeln()

    w.writeln("impl Default for Statechart {")
    w.writeln("  fn default() -> Self {")
    w.writeln("    return Self{")
    w.writeln("      current_state: Default::default(),")
    # w.writeln("      history: Default::default(),")
    # w.writeln("      timers: Default::default(),")
    w.writeln("    };")
    w.writeln("  }")
    w.writeln("}")

    w.writeln("impl Statechart {")
    w.writeln("  fn fair_step(&mut self, event: Option<Event>) {")
    w.writeln("    println!(\"fair step\");")
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
        #      A        ---> And-state
        #    / \   \
        #   S1  S2  S3 ...
        # 
        # (2) The descendants of S, if S is the transition target
        def write_exit(exit_path: List[State]):
            if len(exit_path) == 0:
                w.writeln("%s.exit();" % ident_var(s))
            else:
                s = exit_path[0]
                if isinstance(s, HistoryState):
                    raise Exception("Can't deal with history yet!")
                elif isinstance(s, ParallelState):
                    for c in reversed(s.children):
                        if exit_path[1] is c:
                            write_exit(exit_path[1:]) # continue recursively
                        else:
                            w.writeln("%s.exit();" % ident_var(c))
                elif isinstance(s, State):
                    if s.default_state is not None:
                        # Or-state
                        write_exit(exit_path[1:]) # continue recursively with the next child on the exit path
                w.writeln("%s::exit_actions();" % ident_type(s))

        def write_new_configuration(enter_path: List[State]):
            if len(enter_path) > 0:
                s = enter_path[0]
                if len(enter_path) == 1:
                    # Construct target state.
                    # Whatever the type of parent (And/Or/Basic), just construct the default value:
                    w.writeln("let new_%s: %s = Default::default();" % (ident_var(s), ident_type(s)))
                else:
                    if isinstance(s, ParallelState):
                        for c in s.children:
                            if enter_path[1] is c:
                                write_new_configuration(enter_path[1:]) # recurse
                            else:
                                # Other children's default states are constructed
                                w.writeln("let new_%s: %s = Default::default();" % (ident_var(c), ident_type(c)))
                        # Construct struct
                        w.writeln("let new_%s = %s{%s:%s, ..Default::default()};" % (ident_var(s), ident_type(s), ident_field(enter_path[1]), ident_var(enter_path[1])))

                    elif isinstance(s, State):
                        if len(s.children) > 0:
                            # Or-state
                            write_new_configuration(enter_path[1:]) # recurse
                            w.writeln("let new_%s = %s::%s(new_%s);" % (ident_var(s), ident_type(s), ident_enum_variant(enter_path[1]), ident_var(enter_path[1])))
                        else:
                            # The following should never occur
                            # The parser should have rejected the model before we even get here
                            raise Exception("Basic state in the middle of enter path")

        # Comment of 'write_exit' applies here as well
        def write_enter(enter_path: List[State]):
            if len(enter_path) > 0:
                s = enter_path[0]
                if len(enter_path) == 1:
                    # Target state.
                    w.writeln("%s::enter_default();" % ident_type(s))
                else:
                    if isinstance(s, ParallelState):
                        for c in s.children:
                            if enter_path[1] is c:
                                w.writeln("%s::enter_actions();" % ident_type(c))
                                write_enter(enter_path[1:]) # continue recursively
                            else:
                                w.writeln("%s::enter_default();" % ident_type(c))
                    elif isinstance(s, State):
                        if len(s.children) > 0:
                            # Or-state
                            w.writeln("%s::enter_actions();" & ident_type(s))
                            write_enter(enter_path[1:]) # continue recursively with the next child on the enter path
                        else:
                            # The following should never occur
                            # The parser should have rejected the model before we even get here
                            raise Exception("Basic state in the middle of enter path")

        def parent():
            for t in state.transitions:
                w.writeln("// Outgoing transition")

                if t.trigger is not EMPTY_TRIGGER:
                    if len(t.trigger.enabling) > 1:
                        raise Exception("Multi-event triggers currently unsupported")
                    w.writeln("if let Some(Event::%s) = event {" % t.trigger.enabling[0].name)
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
                    for a in t.actions:
                        w.writeln("println!(%s);" % a.render())

                w.writeln("// Enter actions")
                write_enter(enter_path)

                # 2. Update state

                # A state configuration is just a value
                w.writeln("// Build new state configuration")
                write_new_configuration([t.opt.arena] + enter_path)

                w.writeln("// Update arena configuration")
                w.writeln("*%s = new_%s;" % (ident_var(t.opt.arena), ident_var(t.opt.arena)))

                # This arena is done:
                w.writeln("break '%s;" % (ident_arena_label(t.opt.arena)))

                if t.trigger is not EMPTY_TRIGGER:
                    w.dedent()
                    w.writeln("}")

        def child():
            if isinstance(state, ParallelState):
                for child in state.children:
                    w.writeln("// Orthogonal region")
                    w.writeln("let %s = &mut %s.%s;" % (ident_var(child), ident_var(state), ident_field(child)))
                    write_transitions(child)
            elif isinstance(state, State):
                if state.default_state is not None:
                    w.writeln("'%s: loop {" % ident_arena_label(state))
                    w.indent()
                    w.writeln("match %s {" % ident_var(state))
                    for child in state.children:
                        w.indent()
                        # w.writeln("%s::%s(%s) => {" % (ident_type(state), ident_enum_variant(child), ident_var(child)))
                        w.writeln("%s::%s(_) => {" % (ident_type(state), ident_enum_variant(child)))
                        w.indent()
                        write_transitions(child)
                        w.dedent()
                        w.writeln("},")
                        w.dedent()
                    w.writeln("};")
                    w.writeln("break;")
                    w.dedent()
                    w.writeln("}")

        # TODO: This is where parent/child-first semantic variability should be implemented
        #       For now, it's always "parent first"
        parent()
        child()

    write_transitions(tree.root)

    w.dedent()
    w.dedent()

    w.writeln("  }")
    w.writeln("}")
    w.writeln()


    # # See if it works
    # w.writeln("fn main() {")
    # w.writeln("  let mut sc: Statechart = Default::default();")
    # w.writeln("  Root::enter_default();")
    # w.writeln("  sc.fair_step(None);")
    # w.writeln("  sc.fair_step(None);")
    # w.writeln("}")
    # w.writeln()
