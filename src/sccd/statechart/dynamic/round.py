from typing import *
from sccd.statechart.static.statechart import Statechart
from sccd.statechart.dynamic.event import *
from sccd.util.bitmap import *
from sccd.statechart.static.tree import *
from sccd.util.debug import *
from sccd.common.exceptions import *
from sccd.util import timer

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
                      if (t.source.opt.state_id_bitmap & execution.configuration)
                       and (not forbidden_arenas & t.opt.arena_bitmap) ]

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
                      and (not forbidden_arenas & t.opt.arena_bitmap) ]

    def filter_f(self, execution, enabled_events, events_bitmap):
        return lambda t: (execution.configuration & t.source.opt.state_id_bitmap) and execution.check_guard(t, enabled_events)

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
                      and (t.source.opt.state_id_bitmap & execution.configuration)
                      and (not forbidden_arenas & t.opt.arena_bitmap) ]

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
                    events_bitmap |= t.opt.raised_events
                forbidden_arenas |= t.opt.arena_bitmap
            return transitions

# 1st bitmap: arenas covered by transitions fired
# 2nd bitmap: arenas covered by transitions that had a stable target state
RoundResult = Tuple[Bitmap, Bitmap]

class Round(ABC):
    __slots__ = ["name", "parent", "callbacks", "remainder_events", "next_events"]
    def __init__(self, name):
        self.name = name
        self.parent = None
        
        self.callbacks: List[Callable] = []

        self.remainder_events = [] # events enabled for the remainder of the current round
        self.next_events = [] # events enabled for the entirety of the next round

    def when_done(self, callback):
        self.callbacks.append(callback)

    def run_and_cycle_events(self, forbidden_arenas: Bitmap = Bitmap()) -> RoundResult:
        # with timer.Context("round: %s" % self.name):
            changed, stable = self._run(forbidden_arenas)
            if changed:
                # notify round observers
                for callback in self.callbacks:
                    callback()
                # rotate enabled events
                self.remainder_events = self.next_events
                self.next_events = []
                print_debug("completed "+self.name)
            return (changed, stable)

    def reset(self):
        self.remainder_events = []
        self.next_events = []

    @abstractmethod
    def _run(self, forbidden_arenas: Bitmap) -> RoundResult:
        pass

    def add_remainder_event(self, event: InternalEvent):
        self.remainder_events.append(event)

    def add_next_event(self, event: InternalEvent):
        self.next_events.append(event)

    def enabled_events(self) -> List[InternalEvent]:
        if self.parent:
            return self.remainder_events + self.parent.enabled_events()
        else:
            return self.remainder_events

    def __repr__(self):
        return self.name

class SuperRoundMaximality(ABC):
    __slots__ = []
    @staticmethod
    @abstractmethod
    def forbidden_arenas(arenas_changed: Bitmap, arenas_stabilized: Bitmap) -> Bitmap:
        pass

class TakeOne(SuperRoundMaximality):
    __slots__ = []
    @staticmethod
    def forbidden_arenas(arenas_changed: Bitmap, arenas_stabilized: Bitmap) -> Bitmap:
        return arenas_changed

class TakeMany(SuperRoundMaximality):
    __slots__ = []
    @staticmethod
    def forbidden_arenas(arenas_changed: Bitmap, arenas_stabilized: Bitmap) -> Bitmap:
        return Bitmap()

class Syntactic(SuperRoundMaximality):
    __slots__ = []
    @staticmethod
    def forbidden_arenas(arenas_changed: Bitmap, arenas_stabilized: Bitmap) -> Bitmap:
        return arenas_stabilized

# Examples: Big step, combo step
class SuperRound(Round):
    __slots__ = ["subround", "maximality"]
    def __init__(self, name, subround: Round, maximality: SuperRoundMaximality):
        super().__init__(name)
        self.subround = subround
        subround.parent = self
        self.maximality = maximality

    def __repr__(self):
        return self.name + " > " + self.subround.__repr__()

    def reset(self):
        super().reset()
        self.subround.reset()

    def _run(self, forbidden_arenas: Bitmap) -> RoundResult:
        arenas_changed = Bitmap()
        arenas_stabilized = Bitmap()

        while True:
            changed, stabilized = self.subround.run_and_cycle_events(forbidden_arenas) # no forbidden arenas in subround
            if not changed:
                break # no more transitions could be executed, done!

            arenas_changed |= changed
            arenas_stabilized |= stabilized

            forbidden_arenas |= self.maximality.forbidden_arenas(arenas_changed, arenas_stabilized)

        return (arenas_changed, arenas_stabilized)

# Almost identical to SuperRound, but counts subrounds and raises exception if limit exceeded.
# Useful for maximality options possibly causing infinite big steps like TakeMany and Syntactic.
class SuperRoundWithLimit(SuperRound):
    __slots__ = ["limit"]
    def __init__(self, name, subround: Round, maximality: SuperRoundMaximality, limit: int):
        super().__init__(name, subround, maximality)
        self.limit = limit

    def _run(self, forbidden_arenas: Bitmap) -> RoundResult:
        arenas_changed = Bitmap()
        arenas_stabilized = Bitmap()

        subrounds = 0
        while True:
            changed, stabilized = self.subround.run_and_cycle_events(forbidden_arenas) # no forbidden arenas in subround
            if not changed:
                break # no more transitions could be executed, done!

            subrounds += 1
            if subrounds >= self.limit:
                raise ModelRuntimeError("%s: Limit reached! (%d×%s) Possibly a never-ending big step." % (self.name, subrounds, self.subround.name))

            arenas_changed |= changed
            arenas_stabilized |= stabilized

            forbidden_arenas |= self.maximality.forbidden_arenas(arenas_changed, arenas_stabilized)

        return (arenas_changed, arenas_stabilized)


class SmallStep(Round):
    __slots__ = ["execution", "generator"]
    def __init__(self, name, execution, generator: CandidateGenerator):
        super().__init__(name)
        self.execution = execution
        self.generator = generator

    def _run(self, forbidden_arenas: Bitmap) -> RoundResult:
        enabled_events = self.enabled_events()
        # The cost of sorting our enabled events is smaller than the benefit gained by having to loop less often over it in our transition execution code:
        enabled_events.sort(key=lambda e: e.id)

        transitions = self.generator.generate(self.execution, enabled_events, forbidden_arenas)

        dirty_arenas = Bitmap()
        stable_arenas = Bitmap()

        for t in transitions:
            arena = t.opt.arena_bitmap
            self.execution.fire_transition(enabled_events, t)
            dirty_arenas |= arena
            if t.targets[0].stable:
                stable_arenas |= arena
            enabled_events = self.enabled_events()
            enabled_events.sort(key=lambda e: e.id)

        return (dirty_arenas, stable_arenas)
