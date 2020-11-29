from typing import *
from sccd.statechart.static.tree import *
from sccd.util.visit_tree import *

def ident(state: State) -> str:
    # if bestate.opt.full_name == "/":
        # return ""
    # else:
        return state.opt.full_name.replace('/', '_');

def ident_type(state: State) -> str:
    if state.opt.full_name == "/":
        return "Root" # no technical reason, just make this type 'pop out' a little
    else:
        return "State" + ident(state)

def ident_field(state: State) -> str:
    return "s" + ident(state)


def compile_to_rust(tree: StateTree):
    # 1. Write types

    # 1.1 Write 'current state' types
    def write_state_type(state: State, children: str):
        def as_struct():
            print("struct %s {" % ident_type(state))
            for child in children:
                print("  %s: %s," % (ident_field(child), ident_type(child)))
            print("}")

        def as_enum():
            print("enum %s {" % ident_type(state))
            for child in children:
                print("  %s(%s)," % (ident_field(child), ident_type(child)))
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

    visit_tree(tree.root, lambda s: s.children,
        parent_first=[],
        child_first=[write_state_type])

    # 1.2 Write statechart type
    print("struct Statechart {")
    print("  current_state: %s," % ident_type(tree.root))
    print("  // TODO: history values")
    print("  // TODO: timers")
    print("}")


    # 2. Write "enter default state" functions


    # 3. Write transition functions


    # 4. Write transition candidate generation function