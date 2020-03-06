import termcolor
import functools
from typing import List, Tuple
from enum import Enum
from sccd.runtime.infinity import INFINITY
from sccd.runtime.event_queue import Timestamp
from sccd.runtime.statechart_syntax import *
from sccd.runtime.event import *
from sccd.runtime.semantic_options import *
from sccd.runtime.debug import print_debug
from collections import Counter

ELSE_GUARD = "ELSE_GUARD"
        
class StatechartInstance(Instance):
    def __init__(self, model, object_manager):
        self.model = model
        self.object_manager = object_manager

        # these 2 fields have the same information
        self.configuration = []
        self.configuration_bitmap = 0

        self.eventless_states = 0 # number of states in current configuration that have at least one eventless outgoing transition.

        # mapping from configuration + changed_bitmap to list of possibly allowed transitions
        self.transition_mem = {}
        # mapping from configuration_bitmap (=int) to configuration (=List[State])
        self.config_mem = {}
        # mapping from history state id to states to enter if history is target of transition
        self.history_values = {}

        self._big_step = BigStepState()
        self._combo_step = ComboStepState()
        self._small_step = SmallStepState()

        self.ignore_events = Counter() # Mapping from event name to future times to ignore such event. Used for canceling timers.

    # enter default states, generating a set of output events
    def initialize(self, now: Timestamp) -> Tuple[bool, List[OutputEvent]]:
        states = self.model.root.getEffectiveTargetStates(self)
        self.configuration.extend(states)
        self.configuration_bitmap = sum([2**s.state_id for s in states])
        for state in states:
            print_debug(termcolor.colored('  ENTER %s'%state.name, 'green'))
            self.eventless_states += state.has_eventless_transitions
            self._perform_actions(state.enter)
        stable = not self.eventless_states
        print_debug(termcolor.colored('completed initialization', 'red'))
        return (stable, self._big_step.output_events)

    # perform a big step. generating a set of output events
    def big_step(self, now: Timestamp, input_events: List[Event]) -> Tuple[bool, List[OutputEvent]]:
        filtered = []
        for e in input_events:
            if e.name in self.ignore_events:
                self.ignore_events[e.name] -= 1
            else:
                filtered.append(e)

        self._big_step.next(filtered)
        self._combo_step.reset()
        self._small_step.reset()

        while self.combo_step():
            print_debug(termcolor.colored('completed combo step', 'yellow'))
            self._big_step.has_stepped = True
            if self.model.semantics.big_step_maximality == BigStepMaximality.TAKE_ONE:
                break # Take One -> only one combo step allowed

        if self._big_step.has_stepped:
            print_debug(termcolor.colored('completed big step', 'red'))

        # can the next big step still contain transitions, even if there are no input events?
        stable = not self.eventless_states or (not filtered and not self._big_step.has_stepped)
        return (stable, self._big_step.output_events)

    def combo_step(self):
        self._combo_step.next()
        while self.small_step():
            print_debug(termcolor.colored("completed small step", "blue"))
            self._combo_step.has_stepped = True
        return self._combo_step.has_stepped

    def small_step(self):
        def __younger_than(x, y):
            if x.source in y.source.ancestors:
                return 1
            elif y.source in x.source.ancestors:
                return -1
            else:
                return 0
                
        if self._small_step.has_stepped:
            self._small_step.next()

        candidates = self._transition_candidates()
        if candidates:
            # print_debug(termcolor.colored("small step candidates: "+
            #     str(list(map(
            #         lambda t: "("+str(list(map(
            #             lambda s: "to "+s.name,
            #             t.targets))),
            #         candidates))), 'blue'))
            to_skip = set()
            conflicting = []
            for c1 in candidates:
                if c1 not in to_skip:
                    conflict = [c1]
                    for c2 in candidates[candidates.index(c1):]:
                        if c2.source in c1.source.ancestors or c1.source in c2.source.ancestors:
                            conflict.append(c2)
                            to_skip.add(c2)

                    import functools
                    conflicting.append(sorted(conflict, key=functools.cmp_to_key(__younger_than)))

            if self.model.semantics.concurrency == Concurrency.SINGLE:
                candidate = conflicting[0]
                if self.model.semantics.priority == Priority.SOURCE_PARENT:
                    self._fire_transition(candidate[-1])
                else:
                    self._fire_transition(candidate[0])
            elif self.model.semantics.concurrency == Concurrency.MANY:
                pass # TODO: implement
            self._small_step.has_stepped = True
        return self._small_step.has_stepped

    # @profile
    def _fire_transition(self, t: Transition):

        def __exitSet():
            return [s for s in reversed(t.lca.descendants) if (s in self.configuration)]
        
        def __enterSet(targets):
            target = targets[0]
            for a in reversed(target.ancestors):
                if a in t.source.ancestors:
                    continue
                else:
                    yield a
            for target in targets:
                yield target

        def __getEffectiveTargetStates():
            targets = []
            for target in t.targets:
                for e_t in target.getEffectiveTargetStates(self):
                    if not e_t in targets:
                        targets.append(e_t)
            return targets

        # exit states...
        exit_set = __exitSet()
        for s in exit_set:
            # remember which state(s) we were in if a history state is present
            for h in s.history:
                f = lambda s0: s0.ancestors and s0.parent == s
                if isinstance(h, DeepHistoryState):
                    f = lambda s0: not s0.descendants and s0 in s.descendants
                self.history_values[h.state_id] = list(filter(f, self.configuration))
        print_debug('')
        print_debug(termcolor.colored('transition %s:  %s 🡪 %s'%(self.model._class.name, t.source.name, t.targets[0].name), 'green'))
        for s in exit_set:
            print_debug(termcolor.colored('  EXIT %s' % s.name, 'green'))
            self.eventless_states -= s.has_eventless_transitions
            # execute exit action(s)
            self._perform_actions(s.exit)
            self.configuration_bitmap &= ~2**s.state_id
        
        # combo state changed area
        self._combo_step.changed_bitmap |= 2**t.lca.state_id
        self._combo_step.changed_bitmap |= t.lca.descendant_bitmap
        
        # execute transition action(s)
        self._perform_actions(t.actions)
            
        # enter states...
        targets = __getEffectiveTargetStates()
        enter_set = __enterSet(targets)
        for s in enter_set:
            print_debug(termcolor.colored('  ENTER %s' % s.name, 'green'))
            self.eventless_states += s.has_eventless_transitions
            self.configuration_bitmap |= 2**s.state_id
            # execute enter action(s)
            self._perform_actions(s.enter)
        try:
            self.configuration = self.config_mem[self.configuration_bitmap]
        except:
            self.configuration = self.config_mem[self.configuration_bitmap] = sorted([s for s in list(self.model.states.values()) if 2**s.state_id & self.configuration_bitmap], key=lambda s: s.state_id)
        t.enabled_event = None
        

    # def getChildren(self, link_name):
    #     traversal_list = self.controller.object_manager.processAssociationReference(link_name)
    #     return [i["instance"] for i in self.controller.object_manager.getInstances(self, traversal_list)]

    # def getSingleChild(self, link_name):
    #     return self.getChildren(link_nameself.controller)[0] # assume this will return a single child...

    # Return whether the current configuration includes ALL the states given.
    def inState(self, state_strings: List[str]) -> bool:
        state_ids_bitmap = functools.reduce(lambda x,y: x|y, [2**self.model.states[state_string].state_id for state_string in state_strings])
        in_state = (self.configuration_bitmap | state_ids_bitmap) == self.configuration_bitmap
        if in_state:
            print_debug("in state"+str(state_strings))
        else:
            print_debug("not in state"+str(state_strings))
        return in_state

    # generate transition candidates for current small step
    # @profile
    def _transition_candidates(self) -> List[Transition]:
        changed_bitmap = self._combo_step.changed_bitmap
        key = (self.configuration_bitmap, changed_bitmap)
        try:
            transitions = self.transition_mem[key]
        except:
            self.transition_mem[key] = transitions = [t for s in self.configuration if not (2**s.state_id & changed_bitmap) for t in s.transitions]
        
        enabled_events = self._small_step.current_events + self._combo_step.current_events
        if self.model.semantics.input_event_lifeline == InputEventLifeline.WHOLE or (
            not self._big_step.has_stepped and
                (self.model.semantics.input_event_lifeline == InputEventLifeline.FIRST_COMBO_STEP or (
                not self._combo_step.has_stepped and
                    self.model.semantics.input_event_lifeline == InputEventLifeline.FIRST_SMALL_STEP))):
            enabled_events += self._big_step.input_events
        # print_debug(termcolor.colored("small step enabled events: "+str(list(map(lambda e: e.name, enabled_events))), 'blue'))
        enabled_transitions = []
        for t in transitions:
            if self._is_transition_enabled(t, enabled_events, enabled_transitions):
            # if t.isEnabled(self, enabled_events, enabled_transitions):
                enabled_transitions.append(t)
        return enabled_transitions

    def _is_transition_enabled(self, t, events, enabled_transitions) -> bool:
        if t.trigger is None:
            t.enabled_event = None
            return (t.guard is None) or (t.guard == ELSE_GUARD and not enabled_transitions) or t.guard(self, [])
        else:
            for event in events:
                if (t.trigger.name == event.name and (not t.trigger.port or t.trigger.port == event.port)) and ((t.guard is None) or (t.guard == ELSE_GUARD and not enabled_transitions) or t.guard(event.parameters)):
                    t.enabled_event = event
                    return True

    def _perform_actions(self, actions: List[Action]):
        for a in actions:
            if isinstance(a, RaiseInternalEvent):
                self._raiseInternalEvent(Event(name=a.name, port="", parameters=[]))
            elif isinstance(a, RaiseOutputEvent):
                self._big_step.addOutputEvent(
                    OutputEvent(Event(name=a.name, port=a.outport, parameters=[]),
                    OutputPortTarget(a.outport),
                    a.time_offset))

    def _raiseInternalEvent(self, event):
        if self.model.semantics.internal_event_lifeline == InternalEventLifeline.NEXT_SMALL_STEP:
            self._small_step.addNextEvent(event)
        elif self.model.semantics.internal_event_lifeline == InternalEventLifeline.NEXT_COMBO_STEP:
            self._combo_step.addNextEvent(event)
        elif self.model.semantics.internal_event_lifeline == InternalEventLifeline.QUEUE:
            self._big_step.addOutputEvent(OutputEvent(event, InstancesTarget([self])))


class BigStepState(object):
    def __init__(self):
        self.input_events = [] # input events received from environment before beginning of big step (e.g. from object manager, from input port)
        self.output_events: List[OutputEvent] = []
        self.has_stepped = False

    def next(self, input_events):
        self.input_events = input_events
        self.output_events = []
        self.has_stepped = False

    def addOutputEvent(self, event: OutputEvent):
        self.output_events.append(event)

class ComboStepState(object):
    def __init__(self):
        self.current_events = [] # set of enabled events during combo step
        self.next_events = [] # internal events that were raised during combo step
        self.changed_bitmap = 0 # set of all or-states that were the arena of a triggered transition during big step.
        self.has_stepped = True

    def reset(self):
        self.current_events = []
        self.next_events = []

    def next(self):
        self.current_events = self.next_events
        self.next_events = []
        self.changed_bitmap = 0
        self.has_stepped = False

    def addNextEvent(self, event):
        self.next_events.append(event)


class SmallStepState(object):
    def __init__(self):
        self.current_events = [] # set of enabled events during small step
        self.next_events = [] # events to become 'current' in the next small step
        self.has_stepped = True

    def reset(self):
        self.current_events = []
        self.next_events = []

    def next(self):
        self.current_events = self.next_events # raised events from previous small step
        self.next_events = []
        self.has_stepped = False

    def addNextEvent(self, event):
        self.next_events.append(event)

class Maximality(Enum):
    TAKE_ONE = 0
    TAKE_MANY = 1

class Round:
    def __init__(self, maximality: Maximality):
        self.changed_bitmap: int
        self.current_events: List[Event] = []
        self.next_events: List[Event] = []
        self.has_stepped: bool = True
        self.maximality: Maximality

