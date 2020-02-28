"""
The classes and functions needed to run (compiled) SCCD models.
"""

import os
import termcolor
import functools
from typing import List, Tuple
from enum import Enum
from sccd.runtime.infinity import INFINITY
from sccd.runtime.event_queue import Timestamp
from sccd.runtime.event import Event, OutputEvent, Instance, InstancesTarget
from sccd.runtime.debug import print_debug
from collections import Counter

ELSE_GUARD = "ELSE_GUARD"


class Association(object):
    """
    Class representing an SCCD association.
    """
    def __init__(self, to_class, min_card, max_card):
        """
        Constructor
        
       :param to_class: the name of the target class
       :param min_card: the minimal cardinality
       :param max_card: the maximal cardinality
        """
        self.to_class = to_class
        self.min_card = min_card
        self.max_card = max_card
        self.instances = {} # maps index (as string) to instance
        self.instances_to_ids = {}
        self.size = 0
        self.next_id = 0        

    def allowedToAdd(self):
        return self.max_card == -1 or self.size < self.max_card
        
    def allowedToRemove(self):
        return self.min_card == -1 or self.size > self.min_card
        
    def addInstance(self, instance):
        if self.allowedToAdd():
            new_id = self.next_id
            self.next_id += 1
            self.instances[new_id] = instance
            self.instances_to_ids[instance] = new_id
            self.size += 1
            return new_id
        else:
            raise AssociationException("Not allowed to add the instance to the association.")
        
    def removeInstance(self, instance):
        if self.allowedToRemove():
            index = self.instances_to_ids[instance]
            del self.instances[index]
            del self.instances_to_ids[instance]
            self.size -= 1
            return index
        else:
            raise AssociationException("Not allowed to remove the instance from the association.")
        
    def getInstance(self, index):
        try:
            return self.instances[index]
        except IndexError:
            raise AssociationException("Invalid index for fetching instance(s) from association.")


class StatechartSemantics:
    # Big Step Maximality
    TakeOne = 0
    TakeMany = 1
    # Combo Step Maximality
    ComboTakeOne = 0
    ComboTakeMany = 1
    # Concurrency - not implemented yet
    Single = 0
    Many = 1
    # Preemption - not implemented yet
    NonPreemptive = 0
    Preemptive = 1
    # Internal Event Lifeline
    Queue = 0
    NextSmallStep = 1
    NextComboStep = 2
    # Input Event Lifeline
    Whole = 0
    FirstSmallStep = 1
    FirstComboStep = 2
    # Priority
    SourceParent = 0
    SourceChild = 1
    # TODO: add Memory Protocol options
    
    def __init__(self):
        # default semantics:
        self._big_step_maximality = self.TakeMany
        self.combo_step_maximality = self.TakeOne
        self.internal_event_lifeline = self.Queue
        self.input_event_lifeline = self.FirstComboStep
        self.priority = self.SourceParent
        self.concurrency = self.Single

class State:
    def __init__(self, state_id, name, obj):
        self.state_id = state_id
        self.name = name
        self.obj = obj
        
        self.ancestors = []
        self.descendants = []
        self.descendant_bitmap = 0
        self.children = []
        self.parent = None
        self.enter = None
        self.exit = None
        self.default_state = None
        self.transitions = []
        self.history = []
        self.has_eventless_transitions = False
        
    def getEffectiveTargetStates(self, instance):
        targets = [self]
        if self.default_state:
            targets.extend(self.default_state.getEffectiveTargetStates(instance))
        return targets
        
    def fixTree(self):
        for c in self.children:
            if isinstance(c, HistoryState):
                self.history.append(c)
            c.parent = self
            c.ancestors.append(self)
            c.ancestors.extend(self.ancestors)
            c.fixTree()
        self.descendants.extend(self.children)
        for c in self.children:
            self.descendants.extend(c.descendants)
        for d in self.descendants:
            self.descendant_bitmap |= 2**d.state_id
            
    def addChild(self, child):
        self.children.append(child)
    
    def addTransition(self, transition):
        self.transitions.append(transition)
        
    def setEnter(self, enter):
        self.enter = enter
        
    def setExit(self, exit):
        self.exit = exit
                    
    def __repr__(self):
        return "State(%s)" % (self.state_id)
        
class HistoryState(State):
    def __init__(self, state_id, name, obj):
        State.__init__(self, state_id, name, obj)
        
class ShallowHistoryState(HistoryState):
    def __init__(self, state_id, name, obj):
        HistoryState.__init__(self, state_id, name, obj)
        
    def getEffectiveTargetStates(self, instance):
        if self.state_id in instance.history_values:
            targets = []
            for hv in instance.history_values[self.state_id]:
                targets.extend(hv.getEffectiveTargetStates(instance))
            return targets
        else:
            # TODO: is it correct that in this case, the parent itself is also entered?
            return self.parent.getEffectiveTargetStates(instance)
        
class DeepHistoryState(HistoryState):
    def __init__(self, state_id, name, obj):
        HistoryState.__init__(self, state_id, name, obj)
        
    def getEffectiveTargetStates(self, instance):
        if self.state_id in instance.history_values:
            return instance.history_values[self.state_id]
        else:
            # TODO: is it correct that in this case, the parent itself is also entered?
            return self.parent.getEffectiveTargetStates(instance)
        
class ParallelState(State):
    def __init__(self, state_id, name, obj):
        State.__init__(self, state_id, name, obj)
        
    def getEffectiveTargetStates(self, instance):
        targets = [self]
        for c in self.children:
            if not isinstance(c, HistoryState):
                targets.extend(c.getEffectiveTargetStates(instance))
        return targets
    
class Transition:
    def __init__(self, source, targets):
        self.guard = None
        self.action = None
        self.trigger = None
        self.source = source
        self.targets = targets
        self.enabled_event = None # the event that enabled this transition
        self.optimize()
    
    def isEnabled(self, instance, events, enabled_transitions):
        if self.trigger is None:
            self.enabled_event = None
            return (self.guard is None) or (self.guard == ELSE_GUARD and not enabled_transitions) or self.guard(instance, [])
        else:
            for event in events:
                if (self.trigger.name == event.name and (not self.trigger.port or self.trigger.port == event.port)) and ((self.guard is None) or (self.guard == ELSE_GUARD and not enabled_transitions) or self.guard(event.parameters)):
                    self.enabled_event = event
                    return True
    
    # @profile
    def fire(self, instance):

        def __exitSet():
            return [s for s in reversed(self.lca.descendants) if (s in instance.configuration)]
        
        def __enterSet(targets):
            target = targets[0]
            for a in reversed(target.ancestors):
                if a in self.source.ancestors:
                    continue
                else:
                    yield a
            for target in targets:
                yield target

        def __getEffectiveTargetStates():
            targets = []
            for target in self.targets:
                for e_t in target.getEffectiveTargetStates(instance):
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
                instance.history_values[h.state_id] = list(filter(f, instance.configuration))
        print_debug('')
        print_debug(termcolor.colored('transition %s:  %s 🡪 %s'%(instance.model._class.name, self.source.name, self.targets[0].name), 'green'))
        for s in exit_set:
            print_debug(termcolor.colored('  EXIT %s' % s.name, 'green'))
            instance.eventless_states -= s.has_eventless_transitions
            # execute exit action(s)
            if s.exit:
                s.exit(instance)
            instance.configuration_bitmap &= ~2**s.state_id
        
        # combo state changed area
        instance._combo_step.changed_bitmap |= 2**self.lca.state_id
        instance._combo_step.changed_bitmap |= self.lca.descendant_bitmap
        
        # execute transition action(s)
        if self.action:
            self.action(instance, self.enabled_event.parameters if self.enabled_event else [])
            
        # enter states...
        targets = __getEffectiveTargetStates()
        enter_set = __enterSet(targets)
        for s in enter_set:
            print_debug(termcolor.colored('  ENTER %s' % s.name, 'green'))
            instance.eventless_states += s.has_eventless_transitions
            instance.configuration_bitmap |= 2**s.state_id
            # execute enter action(s)
            if s.enter:
                s.enter(instance)
        try:
            instance.configuration = instance.config_mem[instance.configuration_bitmap]
        except:
            instance.configuration = instance.config_mem[instance.configuration_bitmap] = sorted([s for s in list(instance.model.states.values()) if 2**s.state_id & instance.configuration_bitmap], key=lambda s: s.state_id)
        self.enabled_event = None
                
    def setGuard(self, guard):
        self.guard = guard
        
    def setAction(self, action):
        self.action = action
    
    def setTrigger(self, trigger):
        self.trigger = trigger
        if self.trigger is None:
            self.source.has_eventless_transitions = True
        
    def optimize(self):
        # the least-common ancestor can be computed statically
        if self.source in self.targets[0].ancestors:
            self.lca = self.source
        else:
            self.lca = self.source.parent
            target = self.targets[0]
            if self.source.parent != target.parent: # external
                for a in self.source.ancestors:
                    if a in target.ancestors:
                        self.lca = a
                        break
                    
    def __repr__(self):
        return "Transition(%s, %s)" % (self.source, self.targets[0])

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
            self.eventless_states += state.has_eventless_transitions
            if state.enter:
                state.enter(self)
        stable = not self.eventless_states
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
            if self.model.semantics.big_step_maximality == StatechartSemantics.TakeOne:
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

            if self.model.semantics.concurrency == StatechartSemantics.Single:
                candidate = conflicting[0]
                if self.model.semantics.priority == StatechartSemantics.SourceParent:
                    candidate[-1].fire(self)
                else:
                    candidate[0].fire(self)
            elif self.model.semantics.concurrency == StatechartSemantics.Many:
                pass # TODO: implement
            self._small_step.has_stepped = True
        return self._small_step.has_stepped

    def getChildren(self, link_name):
        traversal_list = self.controller.object_manager.processAssociationReference(link_name)
        return [i["instance"] for i in self.controller.object_manager.getInstances(self, traversal_list)]

    def getSingleChild(self, link_name):
        return self.getChildren(link_nameself.controller)[0] # assume this will return a single child...

    def processBigStepOutput(self):
        # print("processBigStepOutput:", self._big_step.output_events_port)
        self.controller.outputBigStep(self._big_step.output_events_port)
        for e in self._big_step.output_events_om:
            self.controller.object_manager.addEvent(e)

            
    def inState(self, state_strings):
        state_ids = functools.reduce(lambda x,y: x&y, [2**self.model.states[state_string].state_id for state_string in state_strings])
        in_state = (self.configuration_bitmap | state_ids) == self.configuration_bitmap
        if in_state:
            print_debug("in state"+str(state_strings))
        else:
            print_debug("not in state"+str(state_strings))
        return in_state

    # generate transition candidates for current small step
    # @profile
    def _transition_candidates(self):
        changed_bitmap = self._combo_step.changed_bitmap
        key = (self.configuration_bitmap, changed_bitmap)
        try:
            transitions = self.transition_mem[key]
        except:
            self.transition_mem[key] = transitions = [t for s in self.configuration if not (2**s.state_id & changed_bitmap) for t in s.transitions]
        
        enabled_events = self._small_step.current_events + self._combo_step.current_events
        if self.model.semantics.input_event_lifeline == StatechartSemantics.Whole or (
            not self._big_step.has_stepped and
                (self.model.semantics.input_event_lifeline == StatechartSemantics.FirstComboStep or (
                not self._combo_step.has_stepped and
                    self.model.semantics.input_event_lifeline == StatechartSemantics.FirstSmallStep))):
            enabled_events += self._big_step.input_events
        enabled_transitions = []
        for t in transitions:
            if t.isEnabled(self, enabled_events, enabled_transitions):
                enabled_transitions.append(t)
        return enabled_transitions

    def _raiseInternalEvent(self, event):
        if self.model.semantics.internal_event_lifeline == StatechartSemantics.NextSmallStep:
            self._small_step.addNextEvent(event)
        elif self.model.semantics.internal_event_lifeline == StatechartSemantics.NextComboStep:
            self._combo_step.addNextEvent(event)
        elif self.model.semantics.internal_event_lifeline == StatechartSemantics.Queue:
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
    TAKE_MANY = 2

class Round:
    def __init__(self, maximality: Maximality):
        self.changed_bitmap
        self.current_events: List[Event] = []
        self.next_events: List[Event] = []
        self.has_stepped: bool = True
        self.maximality: Maximality

