from typing import *
from dataclasses import *
from abc import *
from sccd.util import timer
from sccd.util.bitmap import *
from sccd.statechart.static.tree import *
from sccd.statechart.dynamic.event import *

@dataclass
class CacheCounter:
    __slots__ = ["cache_hits", "cache_misses"]
    cache_hits: int
    cache_misses: int

ctr = CacheCounter(0, 0)

if timer.TIMINGS:
    import atexit
    def print_stats():
        print("\ncache hits: %s, cache misses: %s" %(ctr.cache_hits, ctr.cache_misses))
    atexit.register(print_stats)


class GeneratorStrategy(ABC):
    __slots__ = ["priority_ordered_transitions"]
    def __init__(self, priority_ordered_transitions):
        self.priority_ordered_transitions = priority_ordered_transitions

    @abstractmethod
    def cache_init(self):
        pass

    @abstractmethod
    def key(self, execution, events_bitmap, forbidden_arenas):
        pass

    @abstractmethod
    def generate(self, execution, events_bitmap, forbidden_arenas):
        pass

    @abstractmethod
    def filter_f(self, execution, enabled_events, events_bitmap):
        pass


# First filter on current state, then filter on current events
class CurrentConfigStrategy(GeneratorStrategy):
    __slots__ = []
    def cache_init(self):
        return {}

    def key(self, execution, events_bitmap, forbidden_arenas):
        return (execution.configuration, forbidden_arenas)

    def generate(self, execution, events_bitmap, forbidden_arenas):
        return [ t for t in self.priority_ordered_transitions
                      if (t.source.state_id_bitmap & execution.configuration)
                       and (not forbidden_arenas & t.arena_bitmap) ]

    def filter_f(self, execution, enabled_events, events_bitmap):
        return lambda t: (not t.trigger or t.trigger.check(events_bitmap)) and execution.check_guard(t, enabled_events)

# First filter based on current events, then filter on current state
class EnabledEventsStrategy(GeneratorStrategy):
    __slots__ = ["statechart"]
    def __init__(self, priority_ordered_transitions, statechart):
        super().__init__(priority_ordered_transitions)
        self.statechart = statechart

    def cache_init(self):
        cache = {}
        cache[(0, 0)] = self.generate(None, 0, 0)
        for event_id in bm_items(self.statechart.internal_events):
            events_bitmap = bit(event_id)
            cache[(events_bitmap, 0)] = self.generate(None, events_bitmap, 0)
        return cache

    def key(self, execution, events_bitmap, forbidden_arenas):
        return (events_bitmap, forbidden_arenas)

    def generate(self, execution, events_bitmap, forbidden_arenas):
        return [ t for t in self.priority_ordered_transitions
                      if (not t.trigger or t.trigger.check(events_bitmap))
                      and (not forbidden_arenas & t.arena_bitmap) ]

    def filter_f(self, execution, enabled_events, events_bitmap):
        return lambda t: (execution.configuration & t.source.state_id_bitmap) and execution.check_guard(t, enabled_events)

class CurrentConfigAndEnabledEventsStrategy(GeneratorStrategy):
    __slots__ = ["statechart"]
    def __init__(self, priority_ordered_transitions, statechart):
        super().__init__(priority_ordered_transitions)
        self.statechart = statechart

    def cache_init(self):
        return {}

    def key(self, execution, events_bitmap, forbidden_arenas):
        return (execution.configuration, events_bitmap, forbidden_arenas)

    def generate(self, execution, events_bitmap, forbidden_arenas):
        return [ t for t in self.priority_ordered_transitions
                      if (not t.trigger or t.trigger.check(events_bitmap))
                      and (t.source.state_id_bitmap & execution.configuration)
                      and (not forbidden_arenas & t.arena_bitmap) ]

    def filter_f(self, execution, enabled_events, events_bitmap):
        return lambda t: execution.check_guard(t, enabled_events)


class CandidateGenerator:
    __slots__ = ["strategy", "cache"]
    def __init__(self, strategy):
        self.strategy = strategy
        self.cache = strategy.cache_init()

    def generate(self, execution, enabled_events: List[InternalEvent], forbidden_arenas: Bitmap) -> List[Transition]:
        with timer.Context("generate candidates"):
            events_bitmap = bm_from_list(e.id for e in enabled_events)
            key = self.strategy.key(execution, events_bitmap, forbidden_arenas)

            try:
                candidates = self.cache[key]
                ctr.cache_hits += 1
            except KeyError:
                candidates = self.cache[key] = self.strategy.generate(execution, events_bitmap, forbidden_arenas)
                ctr.cache_misses += 1

            candidates = filter(self.strategy.filter_f(execution, enabled_events, events_bitmap), candidates)

            if DEBUG:
                candidates = list(candidates) # convert generator to list (gotta do this, otherwise the generator will be all used up by our debug printing
                if candidates:
                    print()
                    if enabled_events:
                        print("events: " + str(enabled_events))
                    print("candidates: " + ",  ".join(str(t) for t in candidates))
                candidates = iter(candidates)

            t = next(candidates, None)
            if t:
                return [t]
            else:
                return []


class ConcurrentCandidateGenerator:
    __slots__ = ["strategy", "cache", "synchronous"]
    def __init__(self, strategy, synchronous):
        self.strategy = strategy
        self.cache = strategy.cache_init()
        self.synchronous = synchronous

    def generate(self, execution, enabled_events: List[InternalEvent], forbidden_arenas: Bitmap) -> List[Transition]:
        with timer.Context("generate candidates"):
            events_bitmap = bm_from_list(e.id for e in enabled_events)
            transitions = []
            while True:
                key = self.strategy.key(execution, events_bitmap, forbidden_arenas)
                try:
                    candidates = self.cache[key]
                    ctr.cache_hits += 1
                except KeyError:
                    candidates = self.cache[key] = self.strategy.generate(execution, events_bitmap, forbidden_arenas)
                    ctr.cache_misses += 1
                candidates = filter(self.strategy.filter_f(execution, enabled_events, events_bitmap), candidates)
                t = next(candidates, None)
                if t:
                    transitions.append(t)
                else:
                    break
                if self.synchronous:
                    events_bitmap |= t.raised_events
                forbidden_arenas |= t.arena_bitmap
            return transitions
