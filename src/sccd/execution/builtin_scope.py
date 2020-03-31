from sccd.syntax.scope import *

builtin_scope = Scope("builtin", None)

def _in_state(ctx: EvalContext, state_list: List[str]) -> bool:
  from sccd.execution.statechart_state import StatechartState

  return StatechartState.in_state(ctx.current_state, state_list)

builtin_scope.add_python_function("INSTATE", _in_state)

def _log10(ctx: EvalContext, i: int) -> float:
  import math
  return math.log10(i)

builtin_scope.add_python_function("log10", _log10)

def _float_to_int(ctx: EvalContext, x: float) -> int:
  return int(x)

builtin_scope.add_python_function("float_to_int", _float_to_int)