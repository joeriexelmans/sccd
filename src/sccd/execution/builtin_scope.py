import math
from sccd.execution.statechart_state import *


builtin_scope = Scope("builtin", None)

def _in_state(ctx: EvalContext, state_list: List[str]) -> bool:
  return StatechartState.in_state(ctx.current_state, state_list)

builtin_scope.add_function("INSTATE", _in_state)

builtin_scope.add_function("log10", lambda _1,_2,_3,i: math.log10(i))
