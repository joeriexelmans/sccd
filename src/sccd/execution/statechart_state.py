from typing import *
from sccd.syntax.statechart import *
from sccd.execution.event import *
from sccd.util.debug import print_debug
from sccd.util.bitmap import *
from sccd.syntax.scope import *


def _in_state(current_state, events, memory, state_list):
  return StatechartState.in_state(current_state, state_list)

builtin_scope = Scope("builtin", None)
builtin_scope.names["INSTATE"] = Variable(offset=0, type=Callable[[List[str]], bool], default_value=_in_state)


# Set of current states etc.
class StatechartState:

  def __init__(self, statechart: Statechart, instance, memory, raise_internal):
    self.model = statechart
    self.instance = instance
    self.memory = memory
    self.raise_internal = raise_internal

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
    self.configuration_bitmap = Bitmap.from_list(s.gen.state_id for s in states)
    for state in states:
        print_debug(termcolor.colored('  ENTER %s'%state.gen.full_name, 'green'))
        self.eventless_states += state.gen.has_eventless_transitions
        self._perform_actions([], state.enter)
        self._start_timers(state.gen.after_triggers)

  def fire_transition(self, events, t: Transition) -> Bitmap:
    def __exitSet():
        return [s for s in reversed(t.gen.lca.gen.descendants) if (s in self.configuration)]
    
    def __enterSet(targets):
        target = targets[0]
        for a in reversed(target.gen.ancestors):
            if a in t.source.gen.ancestors:
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
        for h in s.gen.history:
            f = lambda s0: s0.gen.ancestors and s0.parent == s
            if isinstance(h, DeepHistoryState):
                f = lambda s0: not s0.gen.descendants and s0 in s.gen.descendants
            self.history_values[h.gen.state_id] = list(filter(f, self.configuration))
    # print_debug('')
    print_debug("fire " + str(t))
    for s in exit_set:
        print_debug(termcolor.colored('  EXIT %s' % s.gen.full_name, 'green'))
        self.eventless_states -= s.gen.has_eventless_transitions
        # execute exit action(s)
        self._perform_actions(events, s.exit)
        self.configuration_bitmap &= ~bit(s.gen.state_id)
            
    # execute transition action(s)
    self._perform_actions(events, t.actions)
        
    # enter states...
    targets = __getEffectiveTargetStates()
    enter_set = __enterSet(targets)
    for s in enter_set:
        print_debug(termcolor.colored('  ENTER %s' % s.gen.full_name, 'green'))
        self.eventless_states += s.gen.has_eventless_transitions
        self.configuration_bitmap |= bit(s.gen.state_id)
        # execute enter action(s)
        self._perform_actions(events, s.enter)
        self._start_timers(s.gen.after_triggers)
    try:
        self.configuration = self.config_mem[self.configuration_bitmap]
    except KeyError:
        self.configuration = self.config_mem[self.configuration_bitmap] = [s for s in self.model.tree.state_list if self.configuration_bitmap.has(s.gen.state_id)]

    return t.gen.arena_bitmap

  def check_guard(self, t, events) -> bool:
      # Special case: after trigger
      if isinstance(t.trigger, AfterTrigger):
        e = [e for e in events if e.id == t.trigger.id][0]
        if t.trigger.expected_id != e.parameters[0]:
          return False

      if t.guard is None:
          return True
      else:
          return t.guard.eval(self, events, self.memory)

  def check_source(self, t) -> bool:
      return self.configuration_bitmap.has(t.source.gen.state_id)

  def _perform_actions(self, events, actions: List[Action]):
      for a in actions:
          if isinstance(a, RaiseInternalEvent):
              self.raise_internal(Event(id=a.event_id, name=a.name, port="", parameters=[]))
          elif isinstance(a, RaiseOutputEvent):
              self.output.append(
                  OutputEvent(Event(id=0, name=a.name, port=a.outport, parameters=[]),
                  OutputPortTarget(a.outport),
                  a.time_offset))
          elif isinstance(a, Code):
              a.block.exec(self, events, self.memory)

  def _start_timers(self, triggers: List[AfterTrigger]):
      for after in triggers:
          delay: Duration = after.delay.eval(self, [], self.memory)
          self.output.append(OutputEvent(
              Event(id=after.id, name=after.name, parameters=[after.nextTimerId()]),
              target=InstancesTarget([self.instance]),
              time_offset=delay))

  # Return whether the current configuration includes ALL the states given.
  def in_state(self, state_strings: List[str]) -> bool:
      state_ids_bitmap = Bitmap.from_list((self.model.tree.state_dict[state_string].gen.state_id for state_string in state_strings))
      in_state = self.configuration_bitmap.has_all(state_ids_bitmap)
      # if in_state:
      #     print_debug("in state"+str(state_strings))
      # else:
      #     print_debug("not in state"+str(state_strings))
      return in_state

  def collect_output(self) -> Tuple[bool, List[OutputEvent]]:
    output = self.output
    self.output = []
    return (not self.eventless_states, output)
