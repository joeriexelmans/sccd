from typing import *
import io
import itertools
from sccd.action_lang.codegen.rust import *
from sccd.statechart.static.tree import *
from sccd.util.visit_tree import *
from sccd.statechart.static.statechart import *
from sccd.statechart.static.globals import *
from sccd.statechart.static import priority
from sccd.util.indenting_writer import *

# Hardcoded limit on number of sub-rounds of combo and big step to detect never-ending superrounds.
# TODO: make this a model parameter, also allowing for +infinity
LIMIT = 1000

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
    # and enum variants are scoped locally, so we can use the short name here.
    # Furthermore, the XML parser asserts that state ids are valid identifiers in Rust.
    return "S_" + state.short_name

def ident_field(state: State) -> str:
    return "s" + snake_case(state)

def ident_source_target(state: State) -> str:
    # drop the first '_' (this is safe, the root state itself can never be source or target)
    return snake_case(state)[1:]

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

def ident_event_type(event_name: str) -> str:
    if event_name[0] == '+':
        return "After" + event_name.replace('+', '')
    else:
        return "Event_" + event_name

def ident_event_enum_variant(event_name: str) -> str:
    if event_name[0] == '+':
        return "A" + event_name[1:]
    else:
        return "E_" + event_name

def ident_event_field(event_name: str) -> str:
    if event_name[0] == '+':
        return "a" + event_name[1:]
    else:
        return "e_" + event_name

class StatechartRustGenerator(ActionLangRustGenerator):
    def __init__(self, w, globals):
        super().__init__(w)
        self.globals = globals

        self.parallel_state_cache = {}

        self.tree = None
        self.state_stack = []

        self.trigger = None

    def get_parallel_states(self, state):
        try:
            return self.parallel_state_cache[state]
        except KeyError:
            parallel_states = []
            while state.parent is not None:
                if isinstance(state.parent.type, AndState):
                    for sibling in state.parent.children:
                        if sibling is not state:
                            parallel_states.append(sibling)
                state = state.parent
            self.parallel_state_cache[state] = parallel_states
            return parallel_states

    def get_parallel_states_tuple(self, state):
        parallel_states = self.get_parallel_states(state)
        if len(parallel_states) > 0:
            return "(" + ", ".join("*"+ident_var(s) for s in parallel_states) + ", )"
        else:
            return "()"

    def get_parallel_states_tuple_type(self, state):
        parallel_states = self.get_parallel_states(state)
        if len(parallel_states) > 0:
            return "(%s, )" % ", ".join(ident_type(s) for s in parallel_states)
        else:
            return "()"

    def get_parallel_states_pattern_matched(self, state):
        parallel_states = self.get_parallel_states(state)
        if len(parallel_states) > 0:
            return "(%s, )" % ", ".join("%s: %s" % (ident_var(s), ident_type(s)) for s in parallel_states)
        else:
            return "()"

    def visit_InStateMacroExpansion(self, instate):
        source = instate.ref.source
        target = instate.ref.target

        self.w.writeln("{ // macro expansion for @in(\"%s\")" % target.full_name)
        self.w.indent()

        # Non-exhaustive set of current states, given that 'source' is a current state
        parents = self.get_parallel_states(source)

        # Deconstruct state configuration tuple
        self.w.write("let (")
        for parent in parents:
            self.w.write("ref ")
            self.w.write(ident_var(parent))
            self.w.write(", ")
        self.w.write(") = ")
        self.scope.write_rvalue("@conf", instate.offset, self.w)
        self.w.writeln(";")

        for parent in parents + [source]:
            if is_ancestor(parent=target, child=parent):
                # Special case: target is parent of a current state
                self.w.writeln("true") # Always a current state
                return

            if not is_ancestor(parent=parent, child=target):
                continue # Skip

            # Sequence of states. First is parent. Next is the child of parent on the path to target. Last item is target.
            path = list(self.tree.bitmap_to_states((parent.state_id_bitmap | parent.descendants) & (target.ancestors | target.state_id_bitmap)))

            def write_path(path, target):
                parent = path[0];
                if parent is target:
                    self.w.writeln("true")
                else:
                    child = path[1]
                    if isinstance(parent.type, OrState):
                        self.w.writeln("if let %s::%s(ref %s) = %s {" % (ident_type(parent), ident_enum_variant(child), ident_var(child), ident_var(parent)))
                        self.w.indent()
                        write_path(path[1:], target)
                        self.w.dedent()
                        self.w.writeln("} else { false }")
                    elif isinstance(parent.type, AndState):
                        self.w.writeln("let ref %s = %s.%s;" % (ident_var(child), ident_var(parent), ident_field(child)))
                        write_path(path[1:], target)
                    else:
                        raise Exception("The impossible has happened")

            write_path(path, target)

        self.w.dedent()
        self.w.write("}")

    def visit_SCCDStateConfiguration(self, type):
        self.w.write(self.get_parallel_states_tuple_type(type.state))

    def write_event_params(self, event):
        for param_eval_func in event.params:
            param_eval_func.accept(self) # param eval is a function
            self.w.write("(")
            if self.trigger is not None:
                self.w.write("%s, " % (self.get_parallel_states_tuple(self.state_stack[-1])))
                self.write_trigger_params()
            self.write_parent_call_params(param_eval_func.scope, skip=0) # call it!
            self.w.write("), ")

    def write_trigger_params(self):
        for e in self.trigger.enabling:
            for p in e.params_decl:
                self.w.write("*%s, " % p.name)

    def visit_RaiseOutputEvent(self, raise_event):
        if DEBUG:
            self.w.writeln("eprintln!(\"raise out %s\");" % (raise_event.name))
        self.w.write("(output)(OutEvent::%s(" % (ident_event_enum_variant(raise_event.name)))
        self.write_event_params(raise_event)
        self.w.writeln("));")

    def visit_RaiseInternalEvent(self, raise_event):
        if DEBUG:
            self.w.writeln("eprintln!(\"raise internal %s\");" % (raise_event.name))
        if self.internal_queue:
            self.w.write("sched.set_timeout(%d, InEvent::%s(" % (0, ident_event_enum_variant(raise_event.name)))
            self.write_event_params(raise_event)
            self.w.writeln("));")
        else:
            self.w.write("internal.raise().%s = Some(%s(" % (ident_event_field(raise_event.name), (ident_event_type(raise_event.name))))
            self.write_event_params(raise_event)
            self.w.writeln("));")

    def visit_Code(self, a):
        self.w.write()
        a.block.accept(self) # block is a function
        self.w.write("(") # call it...
        if self.trigger is not None:
            self.w.write("%s, " % self.get_parallel_states_tuple(self.state_stack[-1]))
            self.write_trigger_params()
        self.write_parent_call_params(a.block.scope, skip=0) # call it!
        self.w.writeln(");")

    def visit_State(self, state):
        self.state_stack.append(state)

        # visit children first
        for c in state.real_children:
            c.accept(self)

        # Write 'current state' types
        if isinstance(state.type, AndState):
            self.w.writeln("// And-state")
            # We need Copy for states that will be recorded as history.
            self.w.writeln("#[derive(Default, Copy, Clone)]")
            self.w.writeln("struct %s {" % ident_type(state))
            for child in state.real_children:
                self.w.writeln("  %s: %s," % (ident_field(child), ident_type(child)))
            self.w.writeln("}")
        elif isinstance(state.type, OrState):
            self.w.writeln("// Or-state")
            self.w.writeln("#[derive(Copy, Clone)]")
            self.w.writeln("enum %s {" % ident_type(state))
            for child in state.real_children:
                self.w.writeln("  %s(%s)," % (ident_enum_variant(child), ident_type(child)))
            self.w.writeln("}")

        # Write "default" constructor
        # We use Rust's Default-trait to record default states,
        # this way, constructing a state instance without parameters will initialize it as the default state.
        if isinstance(state.type, OrState):
            self.w.writeln("impl Default for %s {" % ident_type(state))
            self.w.writeln("  fn default() -> Self {")
            self.w.writeln("    Self::%s(Default::default())" % (ident_enum_variant(state.type.default_state)))
            self.w.writeln("  }")
            self.w.writeln("}")

        # Implement trait 'State': enter/exit
        self.w.writeln("impl %s {" % ident_type(state))

        # Enter actions: Executes enter actions of only this state
        self.w.writeln("  fn enter_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {")
        if DEBUG:
            self.w.writeln("    eprintln!(\"enter %s\");" % state.full_name);
        self.w.writeln("    let mut scope = data;")
        self.w.indent(); self.w.indent()
        for a in state.enter:
            a.accept(self)
        self.w.dedent(); self.w.dedent()
        for a in state.after_triggers:
            self.w.writeln("    timers[%d] = sched.set_timeout(%d, InEvent::%s());" % (a.after_id, a.delay.opt, ident_event_enum_variant(a.enabling[0].name)))
        self.w.writeln("  }")

        # Enter actions: Executes exit actions of only this state
        self.w.writeln("  fn exit_actions<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {")
        self.w.writeln("    let mut scope = data;")
        for a in state.after_triggers:
            self.w.writeln("    sched.unset_timeout(&timers[%d]);" % (a.after_id))
        self.w.indent(); self.w.indent()
        for a in state.exit:
            a.accept(self)
        if DEBUG:
            self.w.writeln("    eprintln!(\"exit %s\");" % state.full_name);
        self.w.dedent(); self.w.dedent()
        self.w.writeln("  }")

        # Enter default: Executes enter actions of entering this state and its default substates, recursively
        self.w.writeln("  fn enter_default<Sched: statechart::Scheduler<InEvent=InEvent>>(timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {")
        self.w.writeln("    %s::enter_actions(timers, data, internal, sched, output);" % (ident_type(state)))
        if isinstance(state.type, AndState):
            for child in state.real_children:
                self.w.writeln("    %s::enter_default(timers, data, internal, sched, output);" % (ident_type(child)))
        elif isinstance(state.type, OrState):
            self.w.writeln("    %s::enter_default(timers, data, internal, sched, output);" % (ident_type(state.type.default_state)))
        self.w.writeln("  }")

        # Exit current: Executes exit actions of this state and current children, recursively
        self.w.writeln("  fn exit_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {")
        # first, children (recursion):
        if isinstance(state.type, AndState):
            for child in state.real_children:
                self.w.writeln("    self.%s.exit_current(timers, data, internal, sched, output);" % (ident_field(child)))
        elif isinstance(state.type, OrState):
            self.w.writeln("    match self {")
            for child in state.real_children:
                self.w.writeln("      Self::%s(s) => { s.exit_current(timers, data, internal, sched, output); }," % (ident_enum_variant(child)))
            self.w.writeln("    }")
        # then, parent:
        self.w.writeln("    %s::exit_actions(timers, data, internal, sched, output);" % (ident_type(state)))
        self.w.writeln("  }")

        # Exit current: Executes enter actions of this state and current children, recursively
        self.w.writeln("  fn enter_current<Sched: statechart::Scheduler<InEvent=InEvent>>(&self, timers: &mut Timers<Sched::TimerId>, data: &mut DataModel, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent)) {")
        # first, parent:
        self.w.writeln("    %s::enter_actions(timers, data, internal, sched, output);" % (ident_type(state)))
        # then, children (recursion):
        if isinstance(state.type, AndState):
            for child in state.real_children:
                self.w.writeln("    self.%s.enter_current(timers, data, internal, sched, output);" % (ident_field(child)))
        elif isinstance(state.type, OrState):
            self.w.writeln("    match self {")
            for child in state.real_children:
                self.w.writeln("      Self::%s(s) => { s.enter_current(timers, data, internal, sched, output); }," % (ident_enum_variant(child)))
            self.w.writeln("    }")
        self.w.writeln("  }")

        self.w.writeln("}")
        self.w.writeln()

        self.state_stack.pop()

    def visit_Statechart(self, sc):
        if sc.semantics.concurrency == Concurrency.MANY:
            raise UnsupportedFeature("concurrency")

        if sc.semantics.enabledness_memory_protocol != MemoryProtocol.SMALL_STEP or sc.semantics.assignment_memory_protocol != MemoryProtocol.SMALL_STEP:
            raise UnsupportedFeature("Memory protocol semantics")


        self.scope.push(sc.scope)

        self.w.writeln("use std::ops::Deref;")
        self.w.writeln("use std::ops::DerefMut;")
        self.w.writeln();
        self.w.writeln("use sccd::action_lang;")
        self.w.writeln("use sccd::inherit_struct;")
        self.w.writeln("use sccd::call_closure;")
        self.w.writeln("use sccd::statechart;")
        self.w.writeln("use sccd::statechart::EventLifeline;")
        self.w.writeln();


        priority_ordered_transitions = priority.priority_and_concurrency(sc) # may raise error

        tree = sc.tree
        self.tree = tree

        self.w.writeln("type Timers<TimerId> = [TimerId; %d];" % tree.timer_count)
        self.w.writeln()

        self.internal_queue = sc.semantics.internal_event_lifeline == InternalEventLifeline.QUEUE

        # Write event types
        if self.internal_queue:
            input_events = {key: val for key,val in itertools.chain(sc.in_events.items(), sc.internal_events.items())}
            internal_events = {}
        else:
            input_events = sc.in_events
            internal_events = sc.internal_events

        internal_same_round = (
            sc.semantics.internal_event_lifeline == InternalEventLifeline.REMAINDER or
            sc.semantics.internal_event_lifeline == InternalEventLifeline.SAME)

        self.w.writeln("// Input Events")
        self.w.writeln("#[cfg_attr(target_arch = \"wasm32\", wasm_bindgen)]")
        self.w.writeln("#[derive(Copy, Clone, Debug)]")
        self.w.writeln("pub enum InEvent {")
        for event_name in input_events:
            self.w.write("  %s(" % (ident_event_enum_variant(event_name)))
            for param_type in input_events[event_name]:
                param_type.accept(self)
                self.w.write(", ")
            self.w.writeln("),")
        self.w.writeln("}")
        self.w.writeln()

        self.w.writeln("// Internal Events")
        for event_name in internal_events:
            self.w.write("struct %s(" % ident_event_type(event_name))
            for param_type in internal_events[event_name]:
                param_type.accept(self)
                self.w.write(", ")
            self.w.writeln(");")

        # Implement internal events as a set
        self.w.writeln("#[derive(Default)]")
        self.w.writeln("struct Internal {")
        for event_name in internal_events:
            self.w.writeln("  %s: Option<%s>," % (ident_event_field(event_name), ident_event_type(event_name)))
        self.w.writeln("}")

        if self.internal_queue:
            # Treat internal events like input events
            self.w.writeln("type InternalLifeline = ();") # Unit type
        else:
            if internal_same_round:
                self.w.writeln("type InternalLifeline = statechart::SameRoundLifeline<Internal>;")
            else:
                self.w.writeln("type InternalLifeline = statechart::NextRoundLifeline<Internal>;")
        self.w.writeln()

        # Output events
        # output_event_names = self.globals.out_events.names
        self.w.writeln("// Output Events")
        self.w.writeln("#[cfg_attr(target_arch = \"wasm32\", wasm_bindgen)]")
        self.w.writeln("#[derive(Copy, Clone, Debug, PartialEq, Eq)]")
        self.w.writeln("pub enum OutEvent {")
        for event_name in sc.out_events:
            self.w.write("  %s(" % (ident_event_enum_variant(event_name)))
            for param_type in sc.out_events[event_name]:
                param_type.accept(self)
                self.w.write(", ")
            self.w.writeln("),")
        self.w.writeln("}")
        self.w.writeln()

        syntactic_maximality = (
            sc.semantics.big_step_maximality == Maximality.SYNTACTIC
            or sc.semantics.combo_step_maximality == Maximality.SYNTACTIC)

        # Write arena type
        arenas = {}
        for t in tree.transition_list:
            arenas.setdefault(t.arena, 2**len(arenas))
        for arena, bm in arenas.items():
            for d in tree.bitmap_to_states(arena.descendants):
                bm |= arenas.get(d, 0)
            arenas[arena] = bm
        self.w.writeln("// Transition arenas (bitmap type)")

        for size, typ in [(8, 'u8'), (16, 'u16'), (32, 'u32'), (64, 'u64'), (128, 'u128')]:
            if len(arenas) + 1 <= size:
                self.w.writeln("type Arenas = %s;" % typ)
                break
        else:
            raise UnsupportedFeature("Too many arenas! Cannot fit into an unsigned int.")
        self.w.writeln("const ARENA_NONE: Arenas = 0;")
        for arena, bm in arenas.items():
            self.w.writeln("const %s: Arenas = %s;" % (ident_arena_const(arena), bin(bm)))
        self.w.writeln("const ARENA_UNSTABLE: Arenas = %s; // indicates any transition fired with an unstable target" % bin(2**len(arenas.items())))
        self.w.writeln()

        # Write statechart type
        self.w.writeln("impl<Sched: statechart::Scheduler> Default for Statechart<Sched> {")
        self.w.writeln("  fn default() -> Self {")
        self.w.writeln("    // Initialize data model")
        self.w.writeln("    let scope = action_lang::Empty{};")
        self.w.indent(); self.w.indent();
        if sc.datamodel is not None:
            sc.datamodel.accept(self)
        datamodel_type = self.scope.commit(sc.scope.size(), self.w)
        self.w.dedent(); self.w.dedent();
        self.w.writeln("    Self {")
        self.w.writeln("      configuration: Default::default(),")
        for h in tree.history_states:
            self.w.writeln("      %s: Default::default()," % (ident_history_field(h)))
        self.w.writeln("      timers: Default::default(),")
        self.w.writeln("      data: scope,")
        self.w.writeln("    }")
        self.w.writeln("  }")
        self.w.writeln("}")
        self.w.writeln("type DataModel = %s;" % datamodel_type)
        self.w.writeln("pub struct Statechart<Sched: statechart::Scheduler> {")
        self.w.writeln("  configuration: %s," % ident_type(tree.root))
        # We always store a history value as 'deep' (also for shallow history).
        # TODO: We may save a tiny bit of space in some rare cases by storing shallow history as only the exited child of the Or-state.
        for h in tree.history_states:
            self.w.writeln("  %s: %s," % (ident_history_field(h), ident_type(h.parent)))
        self.w.writeln("  timers: Timers<Sched::TimerId>,")
        self.w.writeln("  data: DataModel,")
        self.w.writeln("}")
        self.w.writeln()

        # Function fair_step: a single "Take One" Maximality 'round' (= nonoverlapping arenas allowed to fire 1 transition)
        self.w.writeln("fn fair_step<Sched: statechart::Scheduler<InEvent=InEvent>>(sc: &mut Statechart<Sched>, input: &mut Option<InEvent>, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent), dirty: Arenas) -> Arenas {")
        self.w.writeln("  let mut fired: Arenas = ARENA_NONE;")
        self.w.writeln("  let mut scope = &mut sc.data;")
        self.w.writeln("  let %s = &mut sc.configuration;" % ident_var(tree.root))
        self.w.indent()

        transitions_written = []
        def write_transitions(state: State):
            self.state_stack.append(state)

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
                if len(exit_path) > 0:
                    s = exit_path[0] # state to exit

                    if len(exit_path) == 1:
                        # Exit s:
                        self.w.writeln("%s.exit_current(&mut sc.timers, scope, internal, sched, output);" % (ident_var(s)))
                    else:
                        # Exit children:
                        if isinstance(s.type, AndState):
                            for c in reversed(s.children):
                                if exit_path[1] is c:
                                    write_exit(exit_path[1:]) # continue recursively
                                else:
                                    self.w.writeln("%s.exit_current(&mut sc.timers, scope, internal, sched, output);" % (ident_var(c)))
                        elif isinstance(s.type, OrState):
                            write_exit(exit_path[1:]) # continue recursively with the next child on the exit path

                        # Exit s:
                        self.w.writeln("%s::exit_actions(&mut sc.timers, scope, internal, sched, output);" % (ident_type(s)))

                    # Store history
                    if s.deep_history:
                        _, _, h = s.deep_history
                        self.w.writeln("sc.%s = *%s; // Store deep history" % (ident_history_field(h), ident_var(s)))
                    if s.shallow_history:
                        _, h = s.shallow_history
                        if isinstance(s.type, AndState):
                            raise Exception("Shallow history makes no sense for And-state!")
                        # Or-state:
                        self.w.writeln("sc.%s = match %s { // Store shallow history" % (ident_history_field(h), ident_var(s)))
                        for c in s.real_children:
                            self.w.writeln("  %s::%s(_) => %s::%s(%s::default())," % (ident_type(s), ident_enum_variant(c), ident_type(s), ident_enum_variant(c), ident_type(c)))
                        self.w.writeln("};")

            # Writes statements that perform enter actions
            # in the correct order (parent, children (first to last)) for given 'enter path'.
            def write_enter(enter_path: List[State]):
                if len(enter_path) > 0:
                    s = enter_path[0] # state to enter
                    if len(enter_path) == 1:
                        # Target state.
                        if isinstance(s, HistoryState):
                            self.w.writeln("sc.%s.enter_current(&mut sc.timers, scope, internal, sched, output); // Enter actions for history state" %(ident_history_field(s)))
                        else:
                            self.w.writeln("%s::enter_default(&mut sc.timers, scope, internal, sched, output);" % (ident_type(s)))
                    else:
                        # Enter s:
                        self.w.writeln("%s::enter_actions(&mut sc.timers, scope, internal, sched, output);" % (ident_type(s)))
                        # Enter children:
                        if isinstance(s.type, AndState):
                            for c in s.children:
                                if enter_path[1] is c:
                                    write_enter(enter_path[1:]) # continue recursively
                                else:
                                    self.w.writeln("%s::enter_default(&mut sc.timers, scope, internal, sched, output);" % (ident_type(c)))
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
                        self.w.writeln("let new_%s: %s = Default::default();" % (ident_var(s), ident_type(s)))
                    else:
                        next_child = enter_path[1]
                        if isinstance(next_child, HistoryState):
                            # No recursion
                            self.w.writeln("let new_%s = sc.%s; // Restore history value" % (ident_var(s), ident_history_field(next_child)))
                        else:
                            if isinstance(s.type, AndState):
                                for c in s.children:
                                    if next_child is c:
                                        write_new_configuration(enter_path[1:]) # recurse
                                    else:
                                        # Other children's default states are constructed
                                        self.w.writeln("let new_%s: %s = Default::default();" % (ident_var(c), ident_type(c)))
                                # Construct struct
                                self.w.writeln("let new_%s = %s{%s:new_%s, ..Default::default()};" % (ident_var(s), ident_type(s), ident_field(next_child), ident_var(next_child)))
                            elif isinstance(s.type, OrState):
                                if len(s.children) > 0:
                                    # Or-state
                                    write_new_configuration(enter_path[1:]) # recurse
                                    # Construct enum value
                                    self.w.writeln("let new_%s = %s::%s(new_%s);" % (ident_var(s), ident_type(s), ident_enum_variant(next_child), ident_var(next_child)))
                                else:
                                    # If the following occurs, there's a bug in this source file
                                    raise Exception("Basic state in the middle of enter path")

            def parent():
                for i, t in enumerate(state.transitions):
                    self.trigger = t.trigger
                    self.w.writeln("// Outgoing transition %d" % i)

                    # If a transition with an overlapping arena that is an ancestor of ours, we wouldn't arrive here because of the "break 'arena_label" statements.
                    # However, an overlapping arena that is a descendant of ours will not have been detected.
                    # Therefore, we must add an addition check in some cases:
                    arenas_to_check = set()
                    for earlier in transitions_written:
                        if is_ancestor(parent=t.arena, child=earlier.arena):
                            arenas_to_check.add(t.arena)

                    if len(arenas_to_check) > 0:
                        self.w.writeln("// A transition may have fired earlier that overlaps with our arena:")
                        self.w.writeln("if fired & (%s) == ARENA_NONE {" % " | ".join(ident_arena_const(a) for a in arenas_to_check))
                        self.w.indent()

                    if t.trigger is not EMPTY_TRIGGER:
                        condition = []
                        for e in t.trigger.enabling:
                            if e.name in input_events:
                                condition.append("let Some(InEvent::%s(%s)) = &input" % (ident_event_enum_variant(e.name), ", ".join(p.name for p in e.params_decl)))
                            elif e.name in internal_events:
                                condition.append("let Some(%s(%s)) = &internal.current().%s" % (ident_event_type(e.name), ", ".join(p.name for p in e.params_decl), ident_event_field(e.name)))
                            else:
                                print(e.name)
                                print(input_events)
                                print(internal_events)
                                raise Exception("Illegal event ID - Bug in SCCD :(")
                        self.w.writeln("if %s {" % " && ".join(condition))
                        self.w.indent()



                    if t.guard is not None:
                        self.w.write("if ")
                        t.guard.accept(self) # guard is a function...
                        self.w.write("(") # call it!
                        self.w.write(self.get_parallel_states_tuple(t.source))
                        self.w.write(", ")
                        self.write_trigger_params()
                        self.write_parent_call_params(t.guard.scope)
                        self.w.write(")")
                        self.w.writeln(" {")
                        self.w.indent()

                    # 1. Execute transition's actions

                    # Path from arena to source, including source but not including arena
                    exit_path_bm = t.arena.descendants & (t.source.state_id_bitmap | t.source.ancestors) # bitmap
                    exit_path = list(tree.bitmap_to_states(exit_path_bm)) # list of states

                    # Path from arena to target, including target but not including arena
                    enter_path_bm = t.arena.descendants & (t.target.state_id_bitmap | t.target.ancestors) # bitmap
                    enter_path = list(tree.bitmap_to_states(enter_path_bm)) # list of states

                    if DEBUG:
                        self.w.writeln("eprintln!(\"fire %s\");" % str(t))

                    self.w.writeln("// Exit actions")
                    write_exit(exit_path)

                    if len(t.actions) > 0:
                        self.w.writeln("// Transition's actions")
                        for a in t.actions:
                            a.accept(self)

                    self.w.writeln("// Enter actions")
                    write_enter(enter_path)

                    # 2. Update state

                    # A state configuration is just a value
                    self.w.writeln("// Build new state configuration")
                    write_new_configuration([t.arena] + enter_path)

                    self.w.writeln("// Update arena configuration")
                    self.w.writeln("*%s = new_%s;" % (ident_var(t.arena), ident_var(t.arena)))

                    if not syntactic_maximality or t.target.stable:
                        self.w.writeln("fired |= %s; // Stable target" % ident_arena_const(t.arena))
                    else:
                        self.w.writeln("fired |= ARENA_UNSTABLE; // Unstable target")

                    if sc.semantics.input_event_lifeline == InputEventLifeline.FIRST_SMALL_STEP:
                        self.w.writeln("// Input Event Lifeline: First Small Step")
                        self.w.writeln("*input = Option::None;")

                    if sc.semantics.internal_event_lifeline == InternalEventLifeline.NEXT_SMALL_STEP:
                        self.w.writeln("// Internal Event Lifeline: Next Small Step")
                        self.w.writeln("internal.cycle();")

                    # This arena is done:
                    self.w.writeln("break '%s;" % (ident_arena_label(t.arena)))

                    if t.guard is not None:
                        self.w.dedent()
                        self.w.writeln("}")

                    if t.trigger is not EMPTY_TRIGGER:
                        self.w.dedent()
                        self.w.writeln("}")

                    if len(arenas_to_check) > 0:
                        self.w.dedent()
                        self.w.writeln("}")

                    transitions_written.append(t)
                    self.trigger = None

            def child():
                # Here is were we recurse and write the transition code for the children of our 'state'.
                if isinstance(state.type, AndState):
                    for child in state.real_children:
                        self.w.writeln("let %s = &mut %s.%s;" % (ident_var(child), ident_var(state), ident_field(child)))
                    for child in state.real_children:
                        self.w.writeln("// Orthogonal region")
                        write_transitions(child)
                elif isinstance(state.type, OrState):
                    if state.type.default_state is not None:
                        if state in arenas:
                            self.w.writeln("if (fired | dirty) & %s == ARENA_NONE {" % ident_arena_const(state))
                            self.w.indent()

                        self.w.writeln("'%s: loop {" % ident_arena_label(state))
                        self.w.indent()
                        self.w.writeln("match *%s {" % ident_var(state))
                        for child in state.real_children:
                            self.w.indent()
                            self.w.writeln("%s::%s(ref mut %s) => {" % (ident_type(state), ident_enum_variant(child), ident_var(child)))
                            self.w.indent()
                            write_transitions(child)
                            self.w.dedent()
                            self.w.writeln("},")
                            self.w.dedent()
                        self.w.writeln("};")
                        self.w.writeln("break;")
                        self.w.dedent()
                        self.w.writeln("}")

                        if state in arenas:
                            self.w.dedent()
                            self.w.writeln("}")

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

            self.state_stack.pop()

        write_transitions(tree.root)

        self.w.dedent()

        if DEBUG:
            self.w.writeln("  eprintln!(\"completed fair_step\");")
        self.w.writeln("  fired")
        self.w.writeln("}")

        # Write combo step and big step function
        def write_stepping_function(name: str, title: str, maximality: Maximality, substep: str, cycle_input: bool, cycle_internal: bool):
            self.w.writeln("fn %s<Sched: statechart::Scheduler<InEvent=InEvent>>(sc: &mut Statechart<Sched>, input: &mut Option<InEvent>, internal: &mut InternalLifeline, sched: &mut Sched, output: &mut impl FnMut(OutEvent), dirty: Arenas) -> Arenas {" % (name))
            self.w.writeln("  // %s Maximality: %s" % (title, maximality))
            if maximality == Maximality.TAKE_ONE:
                self.w.writeln("  %s(sc, input, internal, sched, output, dirty)" % (substep))
            else:
                self.w.writeln("  let mut fired: Arenas = dirty;")
                # self.w.writeln("  let mut e = input;")
                self.w.writeln("  let mut ctr: u16 = 0;")
                self.w.writeln("  loop {")
                if maximality == Maximality.TAKE_MANY:
                    self.w.writeln("    let just_fired = %s(sc, input, internal, sched, output, ARENA_NONE);" % (substep))
                elif maximality == Maximality.SYNTACTIC:
                    self.w.writeln("    let just_fired = %s(sc, input, internal, sched, output, fired);" % (substep))
                self.w.writeln("    if just_fired == ARENA_NONE { // did any transition fire? (incl. unstable)")
                self.w.writeln("      break;")
                self.w.writeln("    }")
                self.w.writeln("    ctr += 1;")
                self.w.writeln("    assert_ne!(ctr, %d, \"too many steps (limit reached)\");" % LIMIT)
                self.w.writeln("    fired |= just_fired;")
                if cycle_input:
                    self.w.writeln("    // Input Event Lifeline: %s" % sc.semantics.input_event_lifeline)
                    self.w.writeln("    *input = Option::None;")
                if cycle_internal:
                    self.w.writeln("    // Internal Event Lifeline: %s" % sc.semantics.internal_event_lifeline)
                    self.w.writeln("    internal.cycle();")
                self.w.writeln("  }")
                if DEBUG:
                    self.w.writeln("  eprintln!(\"completed %s\");" % name)
                self.w.writeln("  fired")
            self.w.writeln("}")

        write_stepping_function("combo_step", "Combo-Step",
            maximality = sc.semantics.combo_step_maximality,
            substep = "fair_step",
            cycle_input = False,
            cycle_internal = False)

        write_stepping_function("big_step", "Big-Step",
            maximality = sc.semantics.big_step_maximality,
            substep = "combo_step",
            cycle_input = sc.semantics.input_event_lifeline == InputEventLifeline.FIRST_COMBO_STEP,
            cycle_internal = sc.semantics.internal_event_lifeline == InternalEventLifeline.NEXT_COMBO_STEP)

        self.w.writeln()

        # Implement 'SC' trait
        self.w.writeln("impl<Sched: statechart::Scheduler<InEvent=InEvent>> statechart::SC for Statechart<Sched> {")
        self.w.writeln("  type InEvent = InEvent;")
        self.w.writeln("  type OutEvent = OutEvent;")
        self.w.writeln("  type Sched = Sched;")
        self.w.writeln()
        self.w.writeln("  fn init(&mut self, sched: &mut Self::Sched, output: &mut impl FnMut(Self::OutEvent)) {")
        self.w.writeln("    %s::enter_default(&mut self.timers, &mut self.data, &mut Default::default(), sched, output)" % (ident_type(tree.root)))
        self.w.writeln("  }")
        self.w.writeln("  fn big_step(&mut self, mut input: Option<InEvent>, sched: &mut Self::Sched, output: &mut impl FnMut(Self::OutEvent)) {")
        self.w.writeln("    let mut internal: InternalLifeline = Default::default();")
        self.w.writeln("    big_step(self, &mut input, &mut internal, sched, output, ARENA_NONE);")
        self.w.writeln("  }")
        self.w.writeln("}")
        self.w.writeln()

        # Write state types
        tree.root.accept(self)

        self.write_decls()

        if DEBUG:
            self.w.writeln("use std::mem::size_of;")
            self.w.writeln("fn debug_print_sizes<Sched: statechart::Scheduler>() {")
            self.w.writeln("  eprintln!(\"------------------------\");")
            self.w.writeln("  eprintln!(\"Semantics: %s\");" % sc.semantics)
            self.w.writeln("  eprintln!(\"------------------------\");")
            self.w.writeln("  eprintln!(\"info: Statechart: {} bytes\", size_of::<Statechart<Sched>>());")
            self.w.writeln("  eprintln!(\"info:   DataModel: {} bytes\", size_of::<DataModel>());")
            self.w.writeln("  eprintln!(\"info:   Timers: {} bytes\", size_of::<Timers<Sched::TimerId>>());")
            self.w.writeln("  eprintln!(\"info:   History: {} bytes\", %s);" % " + ".join(["0"] + list("size_of::<%s>()" % ident_type(h.parent) for h in tree.history_states)))

            def write_state_size(state, indent=0):
                self.w.writeln("  eprintln!(\"info:   %sState %s: {} bytes\", size_of::<%s>());" % ("  "*indent, state.full_name, ident_type(state)))
                for child in state.real_children:
                    write_state_size(child, indent+1)
            write_state_size(tree.root)
            self.w.writeln("  eprintln!(\"info: InEvent: {} bytes\", size_of::<InEvent>());")
            self.w.writeln("  eprintln!(\"info: OutEvent: {} bytes\", size_of::<OutEvent>());")
            self.w.writeln("  eprintln!(\"info: Arenas: {} bytes\", size_of::<Arenas>());")
            self.w.writeln("  eprintln!(\"------------------------\");")
            self.w.writeln("}")
            self.w.writeln()

        self.tree = None
