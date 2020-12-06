from typing import *
from dataclasses import *
from abc import *
from sccd.action_lang.static.expression import *
from sccd.action_lang.static.statement import *
from sccd.statechart.dynamic.event import *

@dataclass
class SCDurationLiteral(DurationLiteral):
    # optimization: to save us from runtime duration conversions,
    # all durations in statechart are divided by model delta,
    # and evaluate to integer instead of duration type.
    opt: Optional[int] = None

    # override
    def eval(self, memory: MemoryInterface):
        return self.opt

    # original behavior of eval
    def as_duration(self):
        return DurationLiteral.eval(self, None)

@dataclass
class EvalContext:
    __slots__ = ["execution", "events", "memory"]
    
    execution: 'StatechartExecution'
    events: List['Event']
    memory: 'MemoryInterface'

@dataclass
class Action(ABC, Visitable):
    @abstractmethod
    def exec(self, ctx: EvalContext):
        pass

    @abstractmethod
    def render(self) -> str:
        pass

@dataclass
class RaiseEvent(Action):
    name: str
    params: List[Expression]


    def _eval_params(self, memory: MemoryInterface) -> List[Any]:
        return [p.eval(memory) for p in self.params]

@dataclass
class RaiseInternalEvent(RaiseEvent):
    event_id: int

    def render(self) -> str:
        return '^'+self.name

    def exec(self, ctx: EvalContext):
        params = self._eval_params(ctx.memory)
        ctx.execution.raise_internal(
            InternalEvent(id=self.event_id, name=self.name, params=params))

@dataclass
class RaiseOutputEvent(RaiseEvent):
    outport: str

    def exec(self, ctx: EvalContext):
        params = self._eval_params(ctx.memory)
        ctx.execution.raise_output(
            OutputEvent(port=self.outport, name=self.name, params=params))

    def render(self) -> str:
        return '^'+self.outport + '.' + self.name

@dataclass
class Code(Action):
    block: Block

    def exec(self, ctx: EvalContext):
        self.block.exec(ctx.memory)

    def render(self) -> str:
        return '/'+self.block.render()
