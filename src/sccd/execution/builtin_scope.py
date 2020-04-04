from sccd.syntax.expression import *
from sccd.util.debug import *
import termcolor

def _in_state(ctx: EvalContext, state_list: List[str]) -> bool:
  from sccd.execution.statechart_state import StatechartState
  return StatechartState.in_state(ctx.current_state, state_list)


def _log10(ctx: EvalContext, i: int) -> float:
  import math
  return math.log10(i)


def _float_to_int(ctx: EvalContext, x: float) -> int:
  return int(x)


def _log(ctx: EvalContext, s: str) -> None:
  print_debug(termcolor.colored("log: ",'blue')+s)


def _int_to_str(ctx: EvalContext, i: int) -> str:
  return str(i)

BuiltIn = Scope("builtin", None)

BuiltIn.declare("INSTATE", SCCDFunction([SCCDArray(SCCDString)], SCCDBool), const=True)
BuiltIn.declare("log10", SCCDFunction([SCCDInt], SCCDFloat), const=True)
BuiltIn.declare("float_to_int", SCCDFunction([SCCDFloat], SCCDInt), const=True)
BuiltIn.declare("log", SCCDFunction([SCCDString]), const=True)
BuiltIn.declare("int_to_str", SCCDFunction([SCCDInt], SCCDString), const=True)

def load_builtins(memory):
  memory.push_frame(BuiltIn)

  memory.current_frame().storage[0] = _in_state
  memory.current_frame().storage[1] = _log10
  memory.current_frame().storage[2] = _float_to_int
  memory.current_frame().storage[3] = _log
  memory.current_frame().storage[4] = _int_to_str
