from typing import *
from sccd.statechart.static.tree import *
from sccd.util.visit_tree import *

def ident(state: State) -> str:
    return state.opt.full_name.replace('/', '_');

def compile_to_rust(tree: StateTree):
    # 1. Write types

    def write_state_type(state: State, children: str):
        if isinstance(state, ParallelState):
            # We use Rust structs for And-states
            print("struct T%s {" % ident(state))
            for child in children:
                print("  s%s: T%s," % (child, child))
            print("}")
        elif isinstance(state, HistoryState):
            print("Skipping HistoryState: ", state.opt.full_name)
        elif isinstance(state, State):
            # Or-state (with children) or Basic state (without children)
            # We use Rust enums (typed unions)
            print("enum T%s {" % ident(state))
            for child in children:
                print("  s%s(T%s)," % (child, child))
            print("}")
        print()
        return ident(state)

    visit_tree(tree.root, lambda s: s.children,
        parent_first=[],
        child_first=[write_state_type])


    # 2. Write "enter default state" functions


    # 3. Write transition functions


    # 4. Write transition candidate generation function