from typing import *
from sccd.statechart.static.tree import *
from sccd.util.visit_tree import *


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
    return "S_" + state.short_name

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


def compile_to_rust(tree: StateTree):

    # Write 'current state' types

    def write_state_type(state: State, children: List[State]):
        if isinstance(state, HistoryState):
            return None # we got no time for pseudo-states!

        def as_struct():
            print("#[allow(non_camel_case_types)]")
            print("struct %s {" % ident_type(state))
            for child in children:
                print("  %s: %s," % (ident_field(child), ident_type(child)))
            print("}")

        def as_enum():
            print("#[allow(non_camel_case_types)]")
            print("enum %s {" % ident_type(state))
            for child in children:
                print("  %s(%s)," % (ident_enum_variant(child), ident_type(child)))
            print("}")

        if isinstance(state, ParallelState):
            print("// And-state")
            as_struct()
        elif isinstance(state, State):
            if len(state.children) > 0:
                print("// Or-state")
                as_enum() # Or-state
            else:
                # Basic state: write as empty struct
                #
                # An empty struct in Rust is a type with one possible value.
                # An empty struct is a Zero-Sized Type.
                #
                # An empty enum is also a valid type in Rust, but no instances
                # of it can be created. Also called an "uninhabited type".
                print("// Basic state")
                as_struct()

            # The above if-else construction hints at the fact that we would have
            # better used empty And-states to model basic states, instead of empty Or-states...

        print()
        return state


    # Write "enter/exit state" functions

    # This fragment should be moved to a library:
    print("pub trait State {")
    print("  fn enter_actions();")
    print("  fn exit_actions();")
    print("  fn enter_default();")
    print("}")
    print()

    def write_enter_exit(state: State, children: List[State]):
        if isinstance(state, HistoryState):
            return None # we got no time for pseudo-states!

        print("impl State for %s {" % ident_type(state))

        print("  fn enter_actions() {")
        print("    // TODO: execute enter actions here")
        print("    println!(\"enter %s\");" % state.opt.full_name);
        print("  }")

        print("  fn exit_actions() {")
        print("    // TODO: execute exit actions here")
        print("    println!(\"exit %s\");" % state.opt.full_name);
        print("  }")

        print("  fn enter_default() {")
        print("    %s::enter_actions();" % ident_type(state))
        if isinstance(state, ParallelState):
            for child in children:
                print("    %s::enter_default();" % ident_type(child))
        else:
            if state.default_state is not None:
                print("    %s::enter_default();" % ident_type(state.default_state))
        print("  }")

        print("}")
        print()
        return state


    # Write "enter default state" functions

    def write_enter_default(state: State, children: List[State]):
        if isinstance(state, HistoryState):
            return None # we got no time for pseudo-states!

        # We use Rust's Default-trait to record default states,
        # this way, constructing a state instance without parameters will initialize it as the default state.

        print("impl Default for %s {" % ident_type(state))
        print("  fn default() -> Self {")

        if isinstance(state, ParallelState):
            print("    return Self {")
            for child in children:
                print("      %s: Default::default()," % (ident_field(child)))
            print("    };")
        elif isinstance(state, State):
            if state.default_state is not None:
                # Or-state
                print("    return Self::%s(Default::default());" % (ident_enum_variant(state.default_state)))
            else:
                # Basic state
                print("    return Self{};")

        print("  }")
        print("}")
        print()
        return state

    visit_tree(tree.root, lambda s: s.children,
        child_first=[
            write_state_type,
            write_enter_exit,
            write_enter_default,
        ])

    # Write statechart type
    print("pub struct Statechart {")
    print("  current_state: %s," % ident_type(tree.root))
    print("  // TODO: history values")
    print("  // TODO: timers")
    print("}")
    print()

    class IndentingWriter:
        def __init__(self, spaces = 0):
            self.spaces = spaces
        def indent(self):
            self.spaces += 2
        def dedent(self):
            self.spaces -= 2
        def print(self, str):
            print(' '*self.spaces + str)

    print("impl Statechart {")
    print("  fn big_step(&mut self) {")
    print("    println!(\"big step\");")
    print("    let %s = &mut self.current_state;" % ident_var(tree.root))

    w = IndentingWriter(4)

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
                w.print("%s.exit();" % ident_var(s))
            else:
                s = exit_path[0]
                if isinstance(s, HistoryState):
                    raise Exception("Can't deal with history yet!")
                elif isinstance(s, ParallelState):
                    for c in reversed(s.children):
                        if exit_path[1] is c:
                            write_exit(exit_path[1:]) # continue recursively
                        else:
                            w.print("%s.exit();" % ident_var(c))
                elif isinstance(s, State):
                    if s.default_state is not None:
                        # Or-state
                        write_exit(exit_path[1:]) # continue recursively with the next child on the exit path
                w.print("%s::exit_actions();" % ident_type(s))

        def write_new_configuration(enter_path: List[State]):
            if len(enter_path) > 0:
                s = enter_path[0]
                if len(enter_path) == 1:
                    # Construct target state.
                    # Whatever the type of parent (And/Or/Basic), just construct the default value:
                    w.print("let new_%s: %s = Default::default();" % (ident_var(s), ident_type(s)))
                else:
                    if isinstance(s, ParallelState):
                        for c in s.children:
                            if enter_path[1] is c:
                                write_new_configuration(enter_path[1:]) # recurse
                            else:
                                # Other children's default states are constructed
                                w.print("let new_%s: %s = Default::default();" % (ident_var(c), ident_type(c)))
                        # Construct struct
                        w.print("let new_%s = %s{%s:%s, ..Default::default()};" % (ident_var(s), ident_type(s), ident_field(enter_path[1]), ident_var(enter_path[1])))

                    elif isinstance(s, State):
                        if len(s.children) > 0:
                            # Or-state
                            write_new_configuration(enter_path[1:]) # recurse
                            w.print("let new_%s = %s::%s(new_%s);" % (ident_var(s), ident_type(s), ident_enum_variant(enter_path[1]), ident_var(enter_path[1])))
                        else:
                            # The following should never occur
                            # The parser should have rejected the model before we even get here
                            raise Exception("Basic state in the middle of enter path")

        def write_enter(enter_path: List[State]):
            if len(enter_path) > 0:
                s = enter_path[0]
                if len(enter_path) == 1:
                    # Target state.
                    w.print("%s::enter_default();" % ident_type(s))
                else:
                    if isinstance(s, ParallelState):
                        for c in s.children:
                            if enter_path[1] is c:
                                w.print("%s::enter_actions();" % ident_type(c))
                                write_enter(enter_path[1:]) # continue recursively
                            else:
                                w.print("%s::enter_default();" % ident_type(c))
                    elif isinstance(s, State):
                        if len(s.children) > 0:
                            # Or-state
                            w.print("%s::enter_actions();" & ident_type(s))
                            write_enter(enter_path[1:]) # continue recursively with the next child on the enter path
                        else:
                            # The following should never occur
                            # The parser should have rejected the model before we even get here
                            raise Exception("Basic state in the middle of enter path")

        def parent():
            for t in state.transitions:
                w.print("// Outgoing transition")
                # TODO: optimize: static calculation for Or-state ancestors of transition's source

                # Path from arena to source, including source but not including arena
                exit_path_bm = t.opt.arena.opt.descendants & (t.source.opt.state_id_bitmap | t.source.opt.ancestors) # bitmap
                exit_path = list(tree.bitmap_to_states(exit_path_bm)) # list of states

                # Path from arena to target, including target but not including arena
                enter_path_bm = t.opt.arena.opt.descendants & (t.target.opt.state_id_bitmap | t.target.opt.ancestors) # bitmap
                enter_path = list(tree.bitmap_to_states(enter_path_bm)) # list of states

                w.print("// Exit states")
                write_exit(exit_path)

                w.print("// TODO: execute transition's actions here")
                w.print("println!(\"%s\");" % str(t))

                w.print("// Construct new states")
                write_new_configuration([t.opt.arena] + enter_path)

                w.print("// Enter states")
                write_enter(enter_path)

                w.print("// Update arena configuration")
                w.print("*%s = new_%s;" % (ident_var(t.opt.arena), ident_var(t.opt.arena)))
                w.print("break '%s;" % (ident_arena_label(t.opt.arena)))

        def child():
            if isinstance(state, ParallelState):
                for child in state.children:
                    w.print("// Orthogonal region")
                    w.print("let %s = &mut %s.%s;" % (ident_var(child), ident_var(state), ident_field(child)))
                    write_transitions(child)
            elif isinstance(state, State):
                if state.default_state is not None:
                    w.print("'%s: loop {" % ident_arena_label(state))
                    w.indent()
                    w.print("match %s {" % ident_var(state))
                    for child in state.children:
                        w.indent()
                        w.print("%s::%s(%s) => {" % (ident_type(state), ident_enum_variant(child), ident_var(child)))
                        w.indent()
                        write_transitions(child)
                        w.dedent()
                        w.print("},")
                        w.dedent()
                    w.print("};")
                    w.print("break;")
                    w.dedent()
                    w.print("}")

        # TODO: This is where parent/child-first semantic variability should be implemented
        #       For now, it's always "parent first"
        parent()
        child()

    write_transitions(tree.root)

    print("  }")
    print("}")
    print()


    # See if it works
    print("fn main() {")
    print("  let mut sc = Statechart{current_state: Default::default()};")
    print("  Root::enter_default();")
    print("  sc.big_step();")
    print("  sc.big_step();")
    # print("  sc.current_state.exit();")
    print("}")
    print()
