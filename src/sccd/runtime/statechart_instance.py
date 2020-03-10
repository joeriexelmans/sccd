import termcolor
import functools
from typing import List, Tuple, Iterable
from sccd.runtime.event_queue import Timestamp
from sccd.runtime.statechart_syntax import *
from sccd.runtime.event import *
from sccd.runtime.semantic_options import *
from sccd.runtime.debug import print_debug
from sccd.runtime.bitmap import *
from sccd.runtime.model import *
from collections import Counter

ELSE_GUARD = "ELSE_GUARD"

class StatechartInstance(Instance):
    def __init__(self, statechart: Statechart, object_manager):
        if statechart.semantics.has_wildcard():
            raise Exception("Model semantics has unexpanded wildcard for some fields.")

        self.statechart = statechart
        self.object_manager = object_manager

        self.data_model = DataModel({
            "INSTATE": Variable(self.inState),
        })

        # these 2 fields have the same information
        self.configuration = []
        self.configuration_bitmap = Bitmap()

        self.event_mem: Dict[Bitmap, List[Transition]] = {} # mapping from set of enabled events to document-ordered list of potentially enabled transitions.

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

    # enter default states, generating a set of output events
    def initialize(self, now: Timestamp) -> Tuple[bool, List[OutputEvent]]:
        states = self.statechart.tree.root.getEffectiveTargetStates(self)
        self.configuration.extend(states)
        self.configuration_bitmap = Bitmap.from_list(s.state_id for s in states)
        for state in states:
            print_debug(termcolor.colored('  ENTER %s'%state.name, 'green'))
            self.eventless_states += state.has_eventless_transitions
            self._perform_actions(state.enter)
            self._start_timers(state.after_triggers)
        stable = not self.eventless_states
        print_debug(termcolor.colored('completed initialization (time=%d)'%now+("(stable)" if stable else ""), 'red'))
        return (stable, self._big_step.output_events)

    # perform a big step. generating a set of output events
    def big_step(self, now: Timestamp, input_events: List[Event]) -> Tuple[bool, List[OutputEvent]]:
        self._big_step.next(input_events)
        self._combo_step.reset()
        self._small_step.reset()

        # print_debug(termcolor.colored('attempt big step, input_events='+str(input_events), 'red'))

        while self.combo_step():
            print_debug(termcolor.colored('completed combo step', 'yellow'))
            self._big_step.has_stepped = True
            if self.statechart.semantics.big_step_maximality == BigStepMaximality.TAKE_ONE:
                break # Take One -> only one combo step allowed

        # can the next big step still contain transitions, even if there are no input events?
        stable = not self.eventless_states or (not input_events and not self._big_step.has_stepped)

        if self._big_step.has_stepped:
            print_debug(termcolor.colored('completed big step (time=%d)'%now+(" (stable)" if stable else ""), 'red'))
        else:
            print_debug(termcolor.colored("(stable)" if stable else "", 'red'))

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

        candidates = self._transition_candidates2()

        # candidates = list(candidates) # convert generator to list (gotta do this, otherwise the generator will be all used up by our debug printing
        # print_debug(termcolor.colored("small step candidates: "+
        #     str(list(map(
        #         lambda t: reduce(lambda x,y:x+y,list(map(
        #             lambda s: "to "+s.name,
        #             t.targets))),
        #         candidates))), 'blue'))

        for c in candidates:
            if self.statechart.semantics.concurrency == Concurrency.SINGLE:
                self._fire_transition(c)
                self._small_step.has_stepped = True
                break
            elif self.statechart.semantics.concurrency == Concurrency.MANY:
                raise Exception("Not implemented!")
        return self._small_step.has_stepped

    # generate transition candidates for current small step
    # @profile
    def _transition_candidates(self) -> Iterable[Transition]:
        # 1. Get all transitions possibly enabled looking only at current configuration
        changed_bitmap = self._combo_step.changed_bitmap
        key = (self.configuration_bitmap, changed_bitmap)
        try:
            transitions = self.transition_mem[key]
        except KeyError:
            # outgoing transitions whose arenas don't overlap with already fired transitions
            self.transition_mem[key] = transitions = [t for s in self.configuration if not changed_bitmap.has(s.state_id) for t in s.transitions]
            if self.statechart.semantics.priority == Priority.SOURCE_CHILD:
                # Transitions are already in parent -> child (depth-first) order
                # Only the first transition of the candidates will be executed.
                # To get SOURCE-CHILD semantics, we simply reverse the list of candidates:
                transitions.reverse()

        # 2. Filter based on guard and event trigger
        enabled_events = self._enabled_events()
        def filter_f(t):
            return self._check_trigger(t, enabled_events) and self._check_guard(t, enabled_events)
        # print_debug(termcolor.colored("small step enabled events: "+str(list(map(lambda e: e.name, enabled_events))), 'blue'))
        return filter(filter_f, transitions)


    # Alternative implementation of candidate generation using mapping from set of enabled events to enabled transitions
    def _transition_candidates2(self) -> Iterable[Transition]:
        enabled_events = self._enabled_events()
        enabled_events_bitmap = Bitmap.from_list(e.id for e in enabled_events)
        changed_bitmap = self._combo_step.changed_bitmap
        key = (enabled_events_bitmap, changed_bitmap)
        try:
            transitions = self.event_mem[key]
        except KeyError:
            self.event_mem[key] = transitions = [t for t in self.statechart.tree.transition_list if (not t.trigger or enabled_events_bitmap.has(t.trigger.id)) and not changed_bitmap.has(t.source.state_id)]
            if self.statechart.semantics.priority == Priority.SOURCE_CHILD:
                # Transitions are already in parent -> child (depth-first) order
                # Only the first transition of the candidates will be executed.
                # To get SOURCE-CHILD semantics, we simply reverse the list of candidates:
                transitions.reverse()

        def filter_f(t):
            return self._check_source(t) and self._check_guard(t, enabled_events)
        return filter(filter_f, transitions)

    def _check_trigger(self, t, events) -> bool:
        if t.trigger is None:
            return True
        else:
            for event in events:
                if (t.trigger.id == event.id and (not t.trigger.port or t.trigger.port == event.port)):
                    return True

    def _check_guard(self, t, events) -> bool:
        if t.guard is None:
            return True
        else:
            return t.guard.eval(events, self.data_model)

    def _check_source(self, t) -> bool:
        return self.configuration_bitmap.has(t.source.state_id)

    # List of current small step enabled events
    def _enabled_events(self) -> List[Event]:
        events = self._small_step.current_events + self._combo_step.current_events
        if self.statechart.semantics.input_event_lifeline == InputEventLifeline.WHOLE or (
            not self._big_step.has_stepped and
                (self.statechart.semantics.input_event_lifeline == InputEventLifeline.FIRST_COMBO_STEP or (
                not self._combo_step.has_stepped and
                    self.statechart.semantics.input_event_lifeline == InputEventLifeline.FIRST_SMALL_STEP))):
            events += self._big_step.input_events
        return events

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
        print_debug(termcolor.colored('transition  %s 🡪 %s'%(t.source.name, t.targets[0].name), 'green'))
        for s in exit_set:
            print_debug(termcolor.colored('  EXIT %s' % s.name, 'green'))
            self.eventless_states -= s.has_eventless_transitions
            # execute exit action(s)
            self._perform_actions(s.exit)
            self.configuration_bitmap &= ~Bit(s.state_id)
        
        # combo state changed area
        self._combo_step.changed_bitmap |= Bit(t.lca.state_id)
        self._combo_step.changed_bitmap |= t.lca.descendant_bitmap
        
        # execute transition action(s)
        self._perform_actions(t.actions)
            
        # enter states...
        targets = __getEffectiveTargetStates()
        enter_set = __enterSet(targets)
        for s in enter_set:
            print_debug(termcolor.colored('  ENTER %s' % s.name, 'green'))
            self.eventless_states += s.has_eventless_transitions
            self.configuration_bitmap |= Bit(s.state_id)
            # execute enter action(s)
            self._perform_actions(s.enter)
            self._start_timers(s.after_triggers)
        try:
            self.configuration = self.config_mem[self.configuration_bitmap]
        except:
            self.configuration = self.config_mem[self.configuration_bitmap] = [s for s in self.statechart.tree.state_list if self.configuration_bitmap.has(s.state_id)]
        # t.enabled_event = None
        
    # def getChildren(self, link_name):
    #     traversal_list = self.controller.object_manager.processAssociationReference(link_name)
    #     return [i["instance"] for i in self.controller.object_manager.getInstances(self, traversal_list)]

    # def getSingleChild(self, link_name):
    #     return self.getChildren(link_nameself.controller)[0] # assume this will return a single child...

    def _perform_actions(self, actions: List[Action]):
        for a in actions:
            if isinstance(a, RaiseInternalEvent):
                self._raiseInternalEvent(Event(id=a.event_id, name=a.name, port="", parameters=[]))
            elif isinstance(a, RaiseOutputEvent):
                self._big_step.addOutputEvent(
                    OutputEvent(Event(id=0, name=a.name, port=a.outport, parameters=[]),
                    OutputPortTarget(a.outport),
                    a.time_offset))

    def _start_timers(self, triggers: List[AfterTrigger]):
        for after in triggers:
            self._big_step.addOutputEvent(OutputEvent(
                Event(id=after.id, name=after.name, parameters=[after.nextTimerId()]),
                target=InstancesTarget([self]),
                time_offset=after.delay))

    def _raiseInternalEvent(self, event):
        if self.statechart.semantics.internal_event_lifeline == InternalEventLifeline.NEXT_SMALL_STEP:
            self._small_step.addNextEvent(event)
        elif self.statechart.semantics.internal_event_lifeline == InternalEventLifeline.NEXT_COMBO_STEP:
            self._combo_step.addNextEvent(event)
        elif self.statechart.semantics.internal_event_lifeline == InternalEventLifeline.QUEUE:
            self._big_step.addOutputEvent(OutputEvent(event, InstancesTarget([self])))

    # Return whether the current configuration includes ALL the states given.
    def inState(self, state_strings: List[str]) -> bool:
        state_ids_bitmap = Bitmap.from_list((self.statechart.tree.states[state_string].state_id for state_string in state_strings))
        in_state = self.configuration_bitmap.has_all(state_ids_bitmap)
        if in_state:
            print_debug("in state"+str(state_strings))
        else:
            print_debug("not in state"+str(state_strings))
        return in_state


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
        self.changed_bitmap = Bitmap() # set of all or-states that were the arena of a triggered transition during big step.
        self.has_stepped = True

    def reset(self):
        self.current_events = []
        self.next_events = []

    def next(self):
        self.current_events = self.next_events
        self.next_events = []
        self.changed_bitmap = Bitmap()
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


# class TakeOneCandidates:
#     def __init__(self):
#         self.mem: Dict[Tuple[int,int], List[Transition]] = {}

#     def get_candidates(configuration_bitmap:int, changed_bitmap:int) -> List[Transition]:
#         try:
#             return self.mem[(configuration_bitmap, changed_bitmap)]
#         except KeyError:


# class AbstractRound(ABC):
#     def __init__(self):
#         self.filter = None

#     @abstractmethod
#     def attempt(self) -> int:
#         pass

# class Round(AbstractRound):
#     def __init__(self, subround: AbstractRound, f=lambda: True):
#         super().__init__()
#         self.subround = subround

#         self.subround.filter = f
#         # self.subround._parent = self
#         self.filter = f

#     def attempt(self, f) -> int:
#         arenas_changed = 0
#         while True:
#             changed = self.subround.attempt()
#             if not changed:
#                 break
#             arenas_changed |= changed
#         return arenas_changed

# class TakeManyRound(Round):
#     def __init__(self, subround: Round):
#         super().__init__()
#         self.subround = subround
#         self.subround._parent = self

#         # state
#         self.arenas_changed = 0

#     def run(self) -> int:
#         self.arenas_changed = 0
#         while True:
#             changed = self.subround.run()
#             if not changed:
#                 break
#             self.arenas_changed |= changed
#         return self.arenas_changed

# class TakeOneRound(TakeManyRound):

#     def is_allowed(self, t: Transition):
#         # No overlap allowed between consecutive transition's arenas
#         # and parent round must allow it.
#         return not (self.arenas_changed & t.arena_bitmap)
#             and super().is_allowed(t)

# # Small Step - Concurrency: Single
# class SmallStepSingle(AbstractRound):
#     def __init__(self, instance: StatechartInstance):
#         super().__init__()
#         self.instance = instance

#     def attempt(self) -> int:
#         candidates = self.instance.get_candidates()
#         for c in candidates:
#             if self.is_allowed(c):
#                 t.fire()
#                 return t.arena_bitmap # good job, all done!
#         return 0
