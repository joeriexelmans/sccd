from dataclasses import *
from sccd.action_lang.static.expression import *
from sccd.statechart.static.state_ref import StateRef

# Macro expansion for @in
@dataclass
class InState(Expression):
    state_refs: List[StateRef]

    offset: Optional[int] = None

    def init_expr(self, scope: Scope) -> SCCDType:
        self.offset, _ = scope.get_rvalue("@conf")
        return SCCDBool

    def get_type(self) -> SCCDType:
        return SCCDBool

    def eval(self, memory: MemoryInterface):
        state_configuration = memory.load(self.offset)
        # print("state_configuration:", state_configuration)
        # print("INSTATE ", [(r.target, r.target.state_id_bitmap) for r in self.state_refs], " ??")
        result = reduce(lambda x,y: x and y, (bool(ref.target.state_id_bitmap & state_configuration) for ref in self.state_refs))
        # print(result)
        return result

    def render(self):
        return "@in(" + ",".join(ref.target.full_name for ref in self.state_refs)
