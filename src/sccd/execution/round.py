from typing import *
from sccd.execution.event import *
from sccd.util.bitmap import *
from sccd.syntax.tree import *
from sccd.util.debug import print_debug

class CandidatesGenerator:
    def __init__(self, reverse: bool):
        self.reverse = reverse
        self.cache = {}

class CandidatesGeneratorCurrentConfigBased(CandidatesGenerator):
    def generate(self, state, enabled_events: List[Event], arenas_changed: Bitmap) -> Iterable[Transition]:
        key = (state.configuration_bitmap, arenas_changed)

        try:
            candidates = self.cache[key]
        except KeyError:
            candidates = self.cache[key] = [
                t for s in state.configuration
                    if (not arenas_changed.has(s.state_id))
                    for t in s.transitions
                ]
            if self.reverse:
                candidates.reverse()

        def check_trigger(t, enabled_events):
            if not t.trigger:
                return True
            for e in enabled_events:
                if t.trigger.id == e.id and (not t.trigger.port or t.trigger.port == e.port):
                    return True
            return False

        def filter_f(t):
            return check_trigger(t, enabled_events) and state.check_guard(t, enabled_events)
        return filter(filter_f, candidates)

class CandidatesGeneratorEventBased(CandidatesGenerator):
    def generate(self, state, enabled_events: List[Event], arenas_changed: Bitmap) -> Iterable[Transition]:
        events_bitmap = Bitmap.from_list(e.id for e in enabled_events)
        key = (events_bitmap, arenas_changed)

        try:
            candidates = self.cache[key]
        except KeyError:
            candidates = self.cache[key] = [
                t for t in state.model.tree.transition_list
                    if (not t.trigger or events_bitmap.has(t.trigger.id)) # todo: check port?
                    and (not arenas_changed.has(t.source.state_id))
                ]
            if self.reverse:
                candidates.reverse()

        def filter_f(t):
            return state.check_source(t) and state.check_guard(t, enabled_events)
        return filter(filter_f, candidates)

class Round(ABC):
    def __init__(self, name):
        self.name = name
        self.parent = None

        self.remainder_events = []
        self.next_events = []

    def run(self, arenas_changed: Bitmap = Bitmap()) -> Bitmap:
        changed = self._internal_run(arenas_changed)
        if changed:
            self.remainder_events = self.next_events
            self.next_events = []
            print_debug("completed "+self.name)
        return changed

    @abstractmethod
    def _internal_run(self, arenas_changed: Bitmap) -> Bitmap:
        pass

    def add_remainder_event(self, event: Event):
        self.remainder_events.append(event)

    def add_next_event(self, event: Event):
        self.next_events.append(event)

    def enabled_events(self) -> List[Event]:
        if self.parent:
            return self.remainder_events + self.parent.enabled_events()
        else:
            return self.remainder_events

    def __repr__(self):
        return self.name

# Examples: Big step, combo step
class SuperRound(Round):
    def __init__(self, name, subround: Round, take_one: bool):
        super().__init__(name)
        self.subround = subround
        subround.parent = self
        self.take_one = take_one
    
    def _internal_run(self, arenas_changed: Bitmap) -> Bitmap:
        while True:
            if self.take_one:
                changed = self.subround.run(arenas_changed)
            else:
                changed = self.subround.run()
            if not changed:
                break
            arenas_changed |= changed
        return arenas_changed

    def __repr__(self):
        return self.name + " > " + self.subround.__repr__()

class SmallStep(Round):
    def __init__(self, name, state, generator: CandidatesGenerator):
        super().__init__(name)
        self.state = state
        self.generator = generator

    def _internal_run(self, arenas_changed: Bitmap) -> Bitmap:
        enabled_events = self.enabled_events()
        candidates = self.generator.generate(self.state, enabled_events, arenas_changed)

        candidates = list(candidates) # convert generator to list (gotta do this, otherwise the generator will be all used up by our debug printing
        if candidates:
            print_debug("")
            if enabled_events:
                print_debug("events: " + str(enabled_events))
            print_debug("candidates: " + str(candidates))

        for t in candidates:
            arenas_changed |= self.state.fire_transition(enabled_events, t)
            return arenas_changed
