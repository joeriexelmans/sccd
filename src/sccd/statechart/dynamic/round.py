from typing import *
from sccd.statechart.dynamic.candidate_generator import *
from sccd.util.debug import *
from sccd.common.exceptions import *
from sccd.util import timer

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

    def __str__(self):
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
    __slots__ = ["subround", "maximality", "limit"]
    def __init__(self, name, subround: Round, maximality: SuperRoundMaximality, limit: Optional[int] = None):
        super().__init__(name)
        self.subround = subround
        subround.parent = self
        self.maximality = maximality
        self.limit = limit

    def __str__(self):
        return self.name + " > " + str(self.subround)

    def _run(self, forbidden_arenas: Bitmap) -> RoundResult:
        arenas_changed = Bitmap()
        arenas_stabilized = Bitmap()

        subrounds = 0
        while True:
            changed, stabilized = self.subround.run_and_cycle_events(forbidden_arenas) # no forbidden arenas in subround
            if not changed:
                break # no more transitions could be executed, done!

            if self.limit is not None:
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
            if t.opt.target_stable:
                stable_arenas |= arena
            enabled_events = self.enabled_events()
            enabled_events.sort(key=lambda e: e.id)

        return (dirty_arenas, stable_arenas)
