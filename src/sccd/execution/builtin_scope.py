from sccd.syntax.scope import *
from sccd.util.debug import *
import termcolor

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

def _log(ctx: EvalContext, s: str):
  print_debug(termcolor.colored("log: ",'blue')+s)

builtin_scope.add_python_function("log", _log)

def _int_to_str(ctx: EvalContext, i: int) -> str:
  return str(i)

builtin_scope.add_python_function("int_to_str", _int_to_str)