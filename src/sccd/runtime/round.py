from typing import *
from sccd.runtime.event import *
from sccd.runtime.bitmap import *
from sccd.runtime.statechart_syntax import *
from sccd.runtime.debug import print_debug

class CandidatesGenerator:
    def __init__(self, instance):
        self.instance = instance
        self.cache = {}

class CandidatesGeneratorEventBased(CandidatesGenerator):
    def generate(self, enabled_events: List[Event], arenas_changed: Bitmap) -> Iterable[Transition]:
        events_bitmap = Bitmap.from_list(e.id for e in enabled_events)
        key = (events_bitmap, arenas_changed)

        candidates = self.cache.setdefault(key, [
            t for t in self.instance.statechart.tree.transition_list
                if (not t.trigger or events_bitmap.has(t.trigger.id)) # todo: check port
                and (not arenas_changed.has(t.source.state_id))
            ])

        def filter_f(t):
            return self.instance._check_source(t) and self.instance._check_guard(t, enabled_events)
        return filter(filter_f, candidates)

class CandidatesGeneratorCurrentConfigBased(CandidatesGenerator):
    def generate(self, enabled_events: List[Event], arenas_changed: Bitmap) -> Iterable[Transition]:
        key = (self.instance.configuration_bitmap, arenas_changed)

        candidates = self.cache.setdefault(key, [
            t for s in self.instance.configuration
                if (not arenas_changed.has(s.state_id))
                for t in s.transitions
            ])

        def check_trigger(t, enabled_events):
            if not t.trigger:
                return True
            for e in enabled_events:
                if t.trigger.id == e.id and (not t.trigger.port or t.trigger.port == e.port):
                    return True
            return False

        def filter_f(t):
            return check_trigger(t, enabled_events) and self.instance._check_guard(t, enabled_events)
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

class SmallStep(Round):
    def __init__(self, name, generator: CandidatesGenerator):
        super().__init__(name)
        self.generator = generator

    def _internal_run(self, arenas_changed: Bitmap) -> Bitmap:
        enabled_events = self.enabled_events()
        print_debug("enabled events: " + str(enabled_events))
        candidates = self.generator.generate(enabled_events, arenas_changed)

        # candidates = list(candidates) # convert generator to list (gotta do this, otherwise the generator will be all used up by our debug printing
        # print_debug(termcolor.colored("small step candidates: "+
        #     str(list(map(
        #         lambda t: reduce(lambda x,y:x+y,list(map(
        #             lambda s: "to "+s.name,
        #             t.targets))),
        #         candidates))), 'blue'))

        for t in candidates:
            arenas_changed |= self.generator.instance._fire_transition(t)
            return arenas_changed
