from typing import *
from sccd.runtime.statechart_syntax import *
from sccd.runtime.model import Statechart
from sccd.runtime.event import *
from sccd.runtime.debug import print_debug

# Set of current states etc.
class StatechartState:

  def __init__(self, statechart: Statechart, instance, raise_internal):
    self.model = statechart
    self.instance = instance
    self.raise_internal = raise_internal

    self.data_model = statechart.datamodel
    self.data_model.names["INSTATE"] = Variable(self.in_state)

    # these 2 fields have the same information
    self.configuration: List[State] = []
    self.configuration_bitmap: Bitmap() = Bitmap()

    self.eventless_states = 0 # number of states in current configuration that have at least one eventless outgoing transition.

    # mapping from configuration_bitmap (=int) to configuration (=List[State])
    self.config_mem = {}
    # mapping from history state id to states to enter if history is target of transition
    self.history_values = {}

    # output events accumulate here until they are collected
    self.output = []

  # enter default states
  def initialize(self):
    states = self.model.tree.root.getEffectiveTargetStates(self)
    self.configuration.extend(states)
    self.configuration_bitmap = Bitmap.from_list(s.state_id for s in states)
    for state in states:
        print_debug(termcolor.colored('  ENTER %s'%state.name, 'green'))
        self.eventless_states += state.has_eventless_transitions
        self.perform_actions([], state.enter)
        self.start_timers(state.after_triggers)

  def fire_transition(self, events, t: Transition) -> Bitmap:
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
    # print_debug('')
    print_debug("fire " + str(t))
    for s in exit_set:
        print_debug(termcolor.colored('  EXIT %s' % s.name, 'green'))
        self.eventless_states -= s.has_eventless_transitions
        # execute exit action(s)
        self.perform_actions(events, s.exit)
        self.configuration_bitmap &= ~Bit(s.state_id)
            
    # execute transition action(s)
    self.perform_actions(events, t.actions)
        
    # enter states...
    targets = __getEffectiveTargetStates()
    enter_set = __enterSet(targets)
    for s in enter_set:
        print_debug(termcolor.colored('  ENTER %s' % s.name, 'green'))
        self.eventless_states += s.has_eventless_transitions
        self.configuration_bitmap |= Bit(s.state_id)
        # execute enter action(s)
        self.perform_actions(events, s.enter)
        self.start_timers(s.after_triggers)
    try:
        self.configuration = self.config_mem[self.configuration_bitmap]
    except:
        self.configuration = self.config_mem[self.configuration_bitmap] = [s for s in self.model.tree.state_list if self.configuration_bitmap.has(s.state_id)]

    return t.arena_bitmap

  def check_guard(self, t, events) -> bool:
      # Special case: after trigger
      if isinstance(t.trigger, AfterTrigger):
        e = [e for e in events if e.id == t.trigger.id][0]
        if t.trigger.expected_id != e.parameters[0]:
          return False

      if t.guard is None:
          return True
      else:
          return t.guard.eval(events, self.data_model)

  def check_source(self, t) -> bool:
      return self.configuration_bitmap.has(t.source.state_id)

  def perform_actions(self, events, actions: List[Action]):
      for a in actions:
          if isinstance(a, RaiseInternalEvent):
              self.raise_internal(Event(id=a.event_id, name=a.name, port="", parameters=[]))
          elif isinstance(a, RaiseOutputEvent):
              self.output.append(
                  OutputEvent(Event(id=0, name=a.name, port=a.outport, parameters=[]),
                  OutputPortTarget(a.outport),
                  a.time_offset))
          elif isinstance(a, Code):
              a.block.exec(events, self.data_model)

  def start_timers(self, triggers: List[AfterTrigger]):
      for after in triggers:
          delay = after.delay.eval([], self.data_model)
          self.output.append(OutputEvent(
              Event(id=after.id, name=after.name, parameters=[after.nextTimerId()]),
              target=InstancesTarget([self.instance]),
              time_offset=delay))

  # Return whether the current configuration includes ALL the states given.
  def in_state(self, state_strings: List[str]) -> bool:
      state_ids_bitmap = Bitmap.from_list((self.model.tree.states[state_string].state_id for state_string in state_strings))
      in_state = self.configuration_bitmap.has_all(state_ids_bitmap)
      if in_state:
          print_debug("in state"+str(state_strings))
      else:
          print_debug("not in state"+str(state_strings))
      return in_state

  def collect_output(self) -> Tuple[bool, List[OutputEvent]]:
    output = self.output
    self.output = []
    return (not self.eventless_states, output)
