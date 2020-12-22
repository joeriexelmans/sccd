from dataclasses import *
from sccd.action_lang.static.expression import *
from sccd.statechart.static.state_ref import StateRef

@dataclass
class InStateMacroExpansion(Expression):
    ref: StateRef

    offset: Optional[int] = None

    def init_expr(self, scope: Scope) -> SCCDType:
        self.offset, _ = scope.get_rvalue("@conf")
        return SCCDBool

    def get_type(self) -> SCCDType:
        return SCCDBool

    def eval(self, memory: MemoryInterface):
        state_configuration = memory.load(self.offset)
        return self.ref.target.state_id_bitmap & state_configuration

    def render(self):
        return "@in(" + self.ref.target.full_name + ')'