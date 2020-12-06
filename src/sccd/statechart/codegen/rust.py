from typing import *
from sccd.statechart.static.tree import *
from sccd.util.visit_tree import *
from sccd.statechart.static.statechart import *
from sccd.statechart.static.globals import *
from sccd.statechart.static import priority
from sccd.util.indenting_writer import *

# Hardcoded limit on number of sub-rounds of combo and big step to detect never-ending superrounds.
# TODO: make this a model parameter
LIMIT = 1000

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
        # after event
        return "After" + event_name.replace('+', '')
    else:
        return "Event_" + event_name

def ident_event_field(event_name: str) -> str:
    return "e_" + event_name

def compile_actions(actions: List[Action], w: IndentingWriter):
    for a in actions:
        if isinstance(a, RaiseOutputEvent):
            # TODO: evaluate event parameters
            w.writeln("(ctrl.output)(OutEvent{port:\"%s\", event:\"%s\"});" % (a.outport, a.name))
        elif isinstance(a, RaiseInternalEvent):
            w.writeln("internal.raise().%s = Some(%s{});" % (ident_event_field(a.name), (ident_event_type(a.name))))
        else:
            raise UnsupportedFeature(str(type(a)))

def compile_statechart(sc: Statechart, globals: Globals, w: IndentingWriter):

    if sc.semantics.concurrency == Concurrency.MANY:
        raise UnsupportedFeature("concurrency")

    priority_ordered_transitions = priority.priority_and_concurrency(sc) # may raise error

    tree = sc.tree

    w.writeln("type Timers = [TimerId; %d];" % tree.timer_count)
    w.writeln()

    # Write event types
    input_events = sc.internal_events & ~sc.internally_raised_events
    internal_events = sc.internally_raised_events

    internal_queue = sc.semantics.internal_event_lifeline == InternalEventLifeline.QUEUE

    if internal_queue:
        raise UnsupportedFeature("queue-like internal event semantics")

    internal_same_round = (
        sc.semantics.internal_event_lifeline == InternalEventLifeline.REMAINDER or
        sc.semantics.internal_event_lifeline == InternalEventLifeline.SAME)

    w.writeln("// Input Events")
    w.writeln("#[derive(Copy, Clone)]")
    w.writeln("enum InEvent {")
    for event_name in (globals.events.names[i] for i in bm_items(input_events)):
        w.writeln("  %s," % ident_event_type(event_name))
    w.writeln("}")

    for event_name in (globals.events.names[i] for i in bm_items(internal_events)):
        w.writeln("// Internal Event")
        w.writeln("struct %s {" % ident_event_type(event_name))
        w.writeln("  // TODO: event parameters")
        w.writeln("}")

    if not internal_queue:
        # Implement internal events as a set
        w.writeln("// Set of (raised) internal events")
        w.writeln("#[derive(Default)]")
        # Bitmap would be more efficient, but for now struct will do:
        w.writeln("struct Internal {")
        for event_name in (globals.events.names[i] for i in bm_items(internal_events)):
            w.writeln("  %s: Option<%s>," % (ident_event_field(event_name), ident_event_type(event_name)))
        w.writeln("}")

        if internal_same_round:
            w.writeln("type InternalLifeline = SameRoundLifeline<Internal>;")
            # w.writeln("struct InternalLifeline {")
            # w.writeln("}")
        else:
            w.writeln("type InternalLifeline = NextRoundLifeline<Internal>;")
    elif internal_type == "queue":
        pass
        # w.writeln("#[derive(Copy, Clone)]")
        # w.writeln("enum Internal {")
        # for event_name in (globals.events.names[i] for i in bm_items(internal_events)):
        #     w.writeln("  %s," % ident_event_type(event_name))
        # w.writeln("}")
    w.writeln()

    # Write 'current state' types
    def write_state_type(state: State, children: List[State]):
        if isinstance(state.type, AndState):
            w.writeln("// And-state")
            # TODO: Only annotate Copy for states that will be recorded by deep history.
            w.writeln("#[derive(Default, Copy, Clone)]")
            w.writeln("struct %s {" % ident_type(state))
            for child in children:
                w.writeln("  %s: %s," % (ident_field(child), ident_type(child)))
            w.writeln("}")
        elif isinstance(state.type, OrState):
            w.writeln("// Or-state")
            w.writeln("#[derive(Copy, Clone)]")
            w.writeln("enum %s {" % ident_type(state))
            for child in children:
                w.writeln("  %s(%s)," % (ident_enum_variant(child), ident_type(child)))
            w.writeln("}")
        return state

    # Write "default" constructor
    def write_default(state: State, children: List[State]):
        # We use Rust's Default-trait to record default states,
        # this way, constructing a state instance without parameters will initialize it as the default state.
        if isinstance(state.type, OrState):
            w.writeln("impl Default for %s {" % ident_type(state))
            w.writeln("  fn default() -> Self {")
            w.writeln("    Self::%s(Default::default())" % (ident_enum_variant(state.type.default_state)))
            w.writeln("  }")
            w.writeln("}")
        return state

    # Implement trait 'State': enter/exit
    def write_enter_exit(state: State, children: List[State]):
        # w.writeln("impl<'a, OutputCallback: FnMut(OutEvent)> State<Timers, Controller<InEvent, OutputCallback>> for %s {" % ident_type(state))
        # w.writeln("impl<'a, OutputCallback: FnMut(OutEvent)> %s {" % ident_type(state))
        w.writeln("impl %s {" % ident_type(state))

        # Enter actions: Executes enter actions of only this state
        # w.writeln("  fn enter_actions(timers: &mut Timers, internal: &mut InternalLifeline, ctrl: &mut Controller<InEvent, OutputCallback>) {")
        w.writeln("  fn enter_actions<OutputCallback: FnMut(OutEvent)>(timers: &mut Timers, internal: &mut InternalLifeline, ctrl: &mut Controller<InEvent, OutputCallback>) {")
        w.writeln("    eprintln!(\"enter %s\");" % state.full_name);
        w.indent(); w.indent()
        compile_actions(state.enter, w)
        w.dedent(); w.dedent()
        for a in state.after_triggers:
            w.writeln("    timers[%d] = ctrl.set_timeout(%d, InEvent::%s);" % (a.after_id, a.delay.opt, ident_event_type(a.enabling[0].name)))
        w.writeln("  }")

        # Enter actions: Executes exit actions of only this state
        # w.writeln("  fn exit_actions(timers: &mut Timers, internal: &mut InternalLifeline, ctrl: &mut Controller<InEvent, OutputCallback>) {")
        w.writeln("  fn exit_actions<OutputCallback: FnMut(OutEvent)>(timers: &mut Timers, internal: &mut InternalLifeline, ctrl: &mut Controller<InEvent, OutputCallback>) {")
        w.writeln("    eprintln!(\"exit %s\");" % state.full_name);
        for a in state.after_triggers:
            w.writeln("    ctrl.unset_timeout(timers[%d]);" % (a.after_id))
        w.indent(); w.indent()
        compile_actions(state.exit, w)
        w.dedent(); w.dedent()
        w.writeln("  }")

        # Enter default: Executes enter actions of entering this state and its default substates, recursively
        # w.writeln("  fn enter_default(timers: &mut Timers, internal: &mut InternalLifeline, ctrl: &mut Controller<InEvent, OutputCallback>) {")
        w.writeln("  fn enter_default<OutputCallback: FnMut(OutEvent)>(timers: &mut Timers, internal: &mut InternalLifeline, ctrl: &mut Controller<InEvent, OutputCallback>) {")
        w.writeln("    %s::enter_actions(timers, internal, ctrl);" % (ident_type(state)))
        if isinstance(state.type, AndState):
            for child in children:
                w.writeln("    %s::enter_default(timers, internal, ctrl);" % (ident_type(child)))
        elif isinstance(state.type, OrState):
            w.writeln("    %s::enter_default(timers, internal, ctrl);" % (ident_type(state.type.default_state)))
        w.writeln("  }")

        # Exit current: Executes exit actions of this state and current children, recursively
        # w.writeln("  fn exit_current(&self, timers: &mut Timers, internal: &mut InternalLifeline, ctrl: &mut Controller<InEvent, OutputCallback>) {")
        w.writeln("  fn exit_current<OutputCallback: FnMut(OutEvent)>(&self, timers: &mut Timers, internal: &mut InternalLifeline, ctrl: &mut Controller<InEvent, OutputCallback>) {")
        # first, children (recursion):
        if isinstance(state.type, AndState):
            for child in children:
                w.writeln("    self.%s.exit_current(timers, internal, ctrl);" % (ident_field(child)))
        elif isinstance(state.type, OrState):
            w.writeln("    match self {")
            for child in children:
                w.writeln("      Self::%s(s) => { s.exit_current(timers, internal, ctrl); }," % (ident_enum_variant(child)))
            w.writeln("    }")
        # then, parent:
        w.writeln("    %s::exit_actions(timers, internal, ctrl);" % (ident_type(state)))
        w.writeln("  }")

        # Exit current: Executes enter actions of this state and current children, recursively
        # w.writeln("  fn enter_current(&self, timers: &mut Timers, internal: &mut InternalLifeline, ctrl: &mut Controller<InEvent, OutputCallback>) {")
        w.writeln("  fn enter_current<OutputCallback: FnMut(OutEvent)>(&self, timers: &mut Timers, internal: &mut InternalLifeline, ctrl: &mut Controller<InEvent, OutputCallback>) {")
        # first, parent:
        w.writeln("    %s::enter_actions(timers, internal, ctrl);" % (ident_type(state)))
        # then, children (recursion):
        if isinstance(state.type, AndState):
            for child in children:
                w.writeln("    self.%s.enter_current(timers, internal, ctrl);" % (ident_field(child)))
        elif isinstance(state.type, OrState):
            w.writeln("    match self {")
            for child in children:
                w.writeln("      Self::%s(s) => { s.enter_current(timers, internal, ctrl); }," % (ident_enum_variant(child)))
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
    w.writeln("// Transition arenas (bitmap type)")
    # if syntactic_maximality:
    for size, typ in [(8, 'u8'), (16, 'u16'), (32, 'u32'), (64, 'u64'), (128, 'u128')]:
        if len(arenas) + 1 <= size:
            w.writeln("type Arenas = %s;" % typ)
            break
    else:
        raise UnsupportedFeature("Too many arenas! Cannot fit into an unsigned int.")
    w.writeln("const ARENA_NONE: Arenas = 0;")
    for arena, bm in arenas.items():
        w.writeln("const %s: Arenas = %s;" % (ident_arena_const(arena), bin(bm)))
    w.writeln("const ARENA_UNSTABLE: Arenas = %s; // indicates any transition fired with an unstable target" % bin(2**len(arenas.items())))
    # else:
    #     w.writeln("type Arenas = bool;")
    #     w.writeln("const ARENA_NONE: Arenas = false;")
    #     for arena, bm in arenas.items():
    #         w.writeln("const %s: Arenas = true;" % ident_arena_const(arena))
    #     w.writeln("const ARENA_UNSTABLE: Arenas = false; // inapplicable to chosen semantics - all transition targets considered stable")
    w.writeln()

    # Write statechart type
    w.writeln("pub struct Statechart {")
    w.writeln("  current_state: %s," % ident_type(tree.root))
    # We always store a history value as 'deep' (also for shallow history).
    # TODO: We may save a tiny bit of space in some rare cases by storing shallow history as only the exited child of the Or-state.
    for h in tree.history_states:
        w.writeln("  %s: %s," % (ident_history_field(h), ident_type(h.parent)))
    w.writeln("  timers: Timers,")
    w.writeln("}")

    w.writeln("impl Default for Statechart {")
    w.writeln("  fn default() -> Self {")
    w.writeln("    Self {")
    w.writeln("      current_state: Default::default(),")
    for h in tree.history_states:
        w.writeln("      %s: Default::default()," % (ident_history_field(h)))
    w.writeln("      timers: Default::default(),")
    w.writeln("    }")
    w.writeln("  }")
    w.writeln("}")
    w.writeln()

    # Function fair_step: a single "Take One" Maximality 'round' (= nonoverlapping arenas allowed to fire 1 transition)
    w.writeln("fn fair_step<OutputCallback: FnMut(OutEvent)>(sc: &mut Statechart, input: Option<InEvent>, internal: &mut InternalLifeline, ctrl: &mut Controller<InEvent, OutputCallback>, dirty: Arenas) -> Arenas {")
    w.writeln("  let mut fired: Arenas = ARENA_NONE;")
    # w.writeln("  let mut fired: Arenas = dirty;")
    w.writeln("  let %s = &mut sc.current_state;" % ident_var(tree.root))
    w.indent()

    transitions_written = []
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
            if len(exit_path) > 0:
                s = exit_path[0] # state to exit

                if len(exit_path) == 1:
                    # Exit s:
                    w.writeln("%s.exit_current(&mut sc.timers, internal, ctrl);" % (ident_var(s)))
                else:
                    # Exit children:
                    if isinstance(s.type, AndState):
                        for c in reversed(s.children):
                            if exit_path[1] is c:
                                write_exit(exit_path[1:]) # continue recursively
                            else:
                                w.writeln("%s.exit_current(&mut sc.timers, internal, ctrl);" % (ident_var(c)))
                    elif isinstance(s.type, OrState):
                        write_exit(exit_path[1:]) # continue recursively with the next child on the exit path

                    # Exit s:
                    w.writeln("%s::exit_actions(&mut sc.timers, internal, ctrl);" % (ident_type(s)))

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

        # Writes statements that perform enter actions
        # in the correct order (parent, children (first to last)) for given 'enter path'.
        def write_enter(enter_path: List[State]):
            if len(enter_path) > 0:
                s = enter_path[0] # state to enter
                if len(enter_path) == 1:
                    # Target state.
                    if isinstance(s, HistoryState):
                        w.writeln("sc.%s.enter_current(&mut sc.timers, internal, ctrl); // Enter actions for history state" %(ident_history_field(s)))
                    else:
                        w.writeln("%s::enter_default(&mut sc.timers, internal, ctrl);" % (ident_type(s)))
                else:
                    # Enter s:
                    w.writeln("%s::enter_actions(&mut sc.timers, internal, ctrl);" % (ident_type(s)))
                    # Enter children:
                    if isinstance(s.type, AndState):
                        for c in s.children:
                            if enter_path[1] is c:
                                write_enter(enter_path[1:]) # continue recursively
                            else:
                                w.writeln("%s::enter_default(&mut sc.timers, internal, ctrl);" % (ident_type(c)))
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

                # If a transition with an overlapping arena that is an ancestor of ours, we wouldn't arrive here because of the "break 'arena_label" statements.
                # However, an overlapping arena that is a descendant of ours will not have been detected.
                # Therefore, we must add an addition check in some cases:
                arenas_to_check = set()
                for earlier in transitions_written:
                    if is_ancestor(parent=t.arena, child=earlier.arena):
                        arenas_to_check.add(t.arena)

                if len(arenas_to_check) > 0:
                    w.writeln("// A transition may have fired earlier that overlaps with our arena:")
                    w.writeln("if fired & (%s) == ARENA_NONE {" % " | ".join(ident_arena_const(a) for a in arenas_to_check))
                    w.indent()

                if t.trigger is not EMPTY_TRIGGER:
                    condition = []
                    for e in t.trigger.enabling:
                        if bit(e.id) & input_events:
                            condition.append("let Some(InEvent::%s) = &input" % ident_event_type(e.name))
                        elif bit(e.id) & internal_events:
                            condition.append("let Some(%s) = &internal.current().%s" % (ident_event_type(e.name), ident_event_field(e.name)))
                        else:
                            # Bug in SCCD :(
                            raise Exception("Illegal event ID")
                    w.writeln("if %s {" % " && ".join(condition))
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

                w.writeln("eprintln!(\"fire %s\");" % str(t))

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
                    w.writeln("fired |= ARENA_UNSTABLE; // Unstable target")

                if sc.semantics.internal_event_lifeline == InternalEventLifeline.NEXT_SMALL_STEP:
                    w.writeln("// Internal Event Lifeline: Next Small Step")
                    w.writeln("internal.cycle();")

                # This arena is done:
                w.writeln("break '%s;" % (ident_arena_label(t.arena)))

                if t.trigger is not EMPTY_TRIGGER:
                    w.dedent()
                    w.writeln("}")

                if len(arenas_to_check) > 0:
                    w.dedent()
                    w.writeln("}")

                transitions_written.append(t)

        def child():
            # Here is were we recurse and write the transition code for the children of our 'state'.
            if isinstance(state.type, AndState):
                for child in state.real_children:
                    w.writeln("let %s = &mut %s.%s;" % (ident_var(child), ident_var(state), ident_field(child)))
                for child in state.real_children:
                    w.writeln("// Orthogonal region")
                    write_transitions(child)
            elif isinstance(state.type, OrState):
                if state.type.default_state is not None:
                    # if syntactic_maximality and state in arenas:
                    #     w.writeln("if dirty & %s == ARENA_NONE {" % ident_arena_const(state))
                    #     w.indent()
                    if state in arenas:
                        w.writeln("if (fired | dirty) & %s == ARENA_NONE {" % ident_arena_const(state))
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

                    if state in arenas:
                        w.dedent()
                        w.writeln("}")
                    # if syntactic_maximality and state in arenas:
                    #     w.dedent()
                    #     w.writeln("}")

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

    w.writeln("  fired")
    w.writeln("}")

    # Write combo step and big step function
    def write_stepping_function(name: str, title: str, maximality: Maximality, substep: str, cycle_input: bool, cycle_internal: bool):
        w.write("fn %s<OutputCallback: FnMut(OutEvent)>(sc: &mut Statechart, input: Option<InEvent>, internal: &mut InternalLifeline, ctrl: &mut Controller<InEvent, OutputCallback>, dirty: Arenas)" % (name))
        w.writeln(" -> Arenas {")
        w.writeln("  let mut ctr: u16 = 0;")
        if maximality == Maximality.TAKE_ONE:
            w.writeln("  // %s Maximality: Take One" % title)
            w.writeln("  %s(sc, input, internal, ctrl, dirty)" % (substep))
        else:
            w.writeln("  let mut fired: Arenas = dirty;")
            w.writeln("  let mut e = input;")
            w.writeln("  loop {")
            if maximality == Maximality.TAKE_MANY:
                w.writeln("    // %s Maximality: Take Many" % title)
                w.writeln("    let just_fired = %s(sc, e, internal, ctrl, ARENA_NONE);" % (substep))
            elif maximality == Maximality.SYNTACTIC:
                w.writeln("    // %s Maximality: Syntactic" % title)
                w.writeln("    let just_fired = %s(sc, e, internal, ctrl, fired);" % (substep))
            w.writeln("    if just_fired == ARENA_NONE { // did any transition fire? (incl. unstable)")
            w.writeln("      break;")
            w.writeln("    }")
            w.writeln("    ctr += 1;")
            # w.writeln("    if ctr >= %d { panic!(\"too many steps (limit reached)\") };" % LIMIT)
            w.writeln("    assert_ne!(ctr, %d, \"too many steps (limit reached)\");" % LIMIT)
            w.writeln("    fired |= just_fired & !ARENA_UNSTABLE; // only record stable arenas")
            if cycle_input:
                w.writeln("    // Input Event Lifeline: %s" % sc.semantics.input_event_lifeline)
                w.writeln("    e = None;")
            if cycle_internal:
                w.writeln("    // Internal Event Lifeline: %s" % sc.semantics.internal_event_lifeline)
                w.writeln("    internal.cycle();")
            w.writeln("  }")
            w.writeln("  fired")
        w.writeln("}")

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

    w.writeln()

    # Implement 'SC' trait
    w.writeln("impl<OutputCallback: FnMut(OutEvent)> SC<InEvent, Controller<InEvent, OutputCallback>> for Statechart {")
    w.writeln("  fn init(&mut self, ctrl: &mut Controller<InEvent, OutputCallback>) {")
    w.writeln("    %s::enter_default(&mut self.timers, &mut Default::default(), ctrl)" % (ident_type(tree.root)))
    w.writeln("  }")
    w.writeln("  fn big_step(&mut self, input: Option<InEvent>, c: &mut Controller<InEvent, OutputCallback>) {")
    w.writeln("    let mut internal: InternalLifeline = Default::default();")
    w.writeln("    big_step(self, input, &mut internal, c, ARENA_NONE);")
    w.writeln("  }")
    w.writeln("}")
    w.writeln()

    if DEBUG:
        w.writeln("use std::mem::size_of;")
        w.writeln("fn debug_print_sizes() {")
        w.writeln("  eprintln!(\"------------------------\");")
        w.writeln("  eprintln!(\"info: Statechart: {} bytes\", size_of::<Statechart>());")
        w.writeln("  eprintln!(\"info: Timers: {} bytes\", size_of::<Timers>());")
        def write_state_size(state):
            w.writeln("  eprintln!(\"info: State %s: {} bytes\", size_of::<%s>());" % (state.full_name, ident_type(state)))
            for child in state.real_children:
                write_state_size(child)
        write_state_size(tree.root)
        w.writeln("  eprintln!(\"info: InEvent: {} bytes\", size_of::<InEvent>());")
        w.writeln("  eprintln!(\"info: OutEvent: {} bytes\", size_of::<OutEvent>());")
        w.writeln("  eprintln!(\"info: Arenas: {} bytes\", size_of::<Arenas>());")
        w.writeln("  eprintln!(\"------------------------\");")
        w.writeln("}")
