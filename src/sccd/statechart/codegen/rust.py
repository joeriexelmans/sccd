from typing import *
from sccd.statechart.static.tree import *
from sccd.util.visit_tree import *

def ident(state: State) -> str:
    return state.opt.full_name.replace('/', '_');

def ident_type(state: State) -> str:
    if state.opt.full_name == "/":
        return "Root" # no technical reason, just make this type 'pop out' a little
    else:
        return "State" + ident(state)

def ident_enum_variant(state: State) -> str:
    # We know the direct children of a state must have unique names relative to each other,
    # and enum variants are scoped locally, so we can use the short name here:
    return "S_" + state.short_name

def ident_field(state: State) -> str:
    return "s" + ident(state)


def compile_to_rust(tree: StateTree):

    # Write 'current state' types

    def write_state_type(state: State, children: List[State]):
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
        elif isinstance(state, HistoryState):
            print("Skipping HistoryState: ", state.opt.full_name)
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



    print("pub trait State {")
    print("  fn enter_actions(&self);")
    print("  fn exit_actions(&self);")
    print("  fn enter(&self);")
    print("  fn exit(&self);")
    print("}")
    print()


    # Write "enter/exit state" functions

    def write_enter_exit(state: State, children: List[State]):
        print("impl State for %s {" % ident_type(state))
        print("  fn enter_actions(&self) {")
        print("    // TODO: execute enter actions")
        print("    println!(\"enter %s\");" % state.opt.full_name);
        print("  }")
        print("  fn exit_actions(&self) {")
        print("    // TODO: execute exit actions")
        print("    println!(\"exit %s\");" % state.opt.full_name);
        print("  }")
        print("  fn enter(&self) {")
        print("    self.enter_actions();")
        if isinstance(state, ParallelState):
            for child in children:
                print("    self.%s.enter();" % ident_field(child))
        elif isinstance(state, State):
            if len(children) > 0:
                print("    match self {")
                for child in children:
                    print("      Self::%s(s) => s.enter()," % ident_enum_variant(child))
                print("    }")
        print("  }")
        print("  fn exit(&self) {")
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

    # 3 Write statechart type
    print("pub struct Statechart {")
    print("  current_state: %s," % ident_type(tree.root))
    print("  // TODO: history values")
    print("  // TODO: timers")
    print("}")
    print()


    print("fn main() {")
    print("  let sc = Statechart{current_state: Default::default()};")
    print("  sc.current_state.enter();")
    print("}")
    print()


    # 3. Write transition functions


    # 4. Write transition candidate generation function