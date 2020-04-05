from typing import *
from dataclasses import *
from abc import *
from sccd.action_lang.static.expression import *
from sccd.action_lang.static.statement import *
from sccd.statechart.dynamic.event import *

@dataclass
class EvalContext:
    current_state: 'StatechartState'
    events: List['Event']
    memory: 'MemoryInterface'

@dataclass
class Action(ABC):
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

    # just a simple string representation for rendering a transition label
    def render(self) -> str:
        return '^'+self.name

    def _eval_params(self, memory: MemoryInterface) -> List[Any]:
        return [p.eval(memory) for p in self.params]

@dataclass
class RaiseInternalEvent(RaiseEvent):
    event_id: int

    def exec(self, ctx: EvalContext):
        params = self._eval_params(ctx.memory)
        ctx.current_state.raise_internal(
            Event(id=self.event_id, name=self.name, port="", params=params))

@dataclass
class RaiseOutputEvent(RaiseEvent):
    outport: str
    time_offset: int

    def exec(self, ctx: EvalContext):
        params = self._eval_params(ctx.memory)
        ctx.current_state.output.append(
            OutputEvent(Event(id=0, name=self.name, port=self.outport, params=params),
                    OutputPortTarget(self.outport),
                    self.time_offset))

    def render(self) -> str:
        return '^'+self.outport + '.' + self.name

@dataclass
class Code(Action):
    block: Block

    def exec(self, ctx: EvalContext):
        self.block.exec(ctx.memory)

    def render(self) -> str:
        return '/'+self.block.render()
