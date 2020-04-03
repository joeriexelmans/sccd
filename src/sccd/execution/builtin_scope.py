from sccd.syntax.scope import *
from sccd.util.debug import *
import termcolor

builtin_scope = Scope("builtin", None)

def _in_state(ctx: EvalContext, state_list: List[str]) -> bool:
  from sccd.execution.statechart_state import StatechartState

  return StatechartState.in_state(ctx.current_state, state_list)

builtin_scope.add_constant("INSTATE", _in_state, SCCDFunction([SCCDArray(SCCDString)], SCCDBool))

def _log10(ctx: EvalContext, i: int) -> float:
  import math
  return math.log10(i)

builtin_scope.add_constant("log10", _log10, SCCDFunction([SCCDInt], SCCDFloat))

def _float_to_int(ctx: EvalContext, x: float) -> int:
  return int(x)

builtin_scope.add_constant("float_to_int", _float_to_int, SCCDFunction([SCCDFloat], SCCDInt))

def _log(ctx: EvalContext, s: str) -> None:
  print_debug(termcolor.colored("log: ",'blue')+s)

builtin_scope.add_constant("log", _log, SCCDFunction([SCCDString]))

def _int_to_str(ctx: EvalContext, i: int) -> str:
  return str(i)

builtin_scope.add_constant("int_to_str", _int_to_str, SCCDFunction([SCCDInt], SCCDString))
