from sccd.action_lang.static.expression import *
from sccd.util.debug import *

# Builtin "global" functions in statechart language

BuiltIn = Scope("builtin", None)

# The way we add our builtin functions is a bit hackish because they are implemented
# "natively" in Python, rather than in action language code.

BuiltIn.declare("INSTATE", SCCDFunction([SCCDArray(SCCDString)], SCCDBool), const=True)
BuiltIn.declare("log10", SCCDFunction([SCCDInt], SCCDFloat), const=True)
BuiltIn.declare("float_to_int", SCCDFunction([SCCDFloat], SCCDInt), const=True)
BuiltIn.declare("log", SCCDFunction([SCCDString]), const=True)
BuiltIn.declare("int_to_str", SCCDFunction([SCCDInt], SCCDString), const=True)

def load_builtins(memory: MemoryInterface, state):
  import math
  import termcolor
  
  memory.push_frame(BuiltIn)

  # Wrapper functions of the signature expected by the action language:

  def in_state(memory: MemoryInterface, state_list: List[str]) -> bool:
    return state.in_state(state_list)

  def log10(memory: MemoryInterface, i: int) -> float:
    return math.log10(i)

  def float_to_int(memory: MemoryInterface, x: float) -> int:
    return int(x)

  def log(memory: MemoryInterface, s: str) -> None:
    print(termcolor.colored("log: ",'blue')+s)

  def int_to_str(memory: MemoryInterface, i: int) -> str:
    return str(i)

  # Manually write wrapper functions to memory:

  frame = memory.current_frame()

  frame.storage[0] = in_state
  frame.storage[1] = log10
  frame.storage[2] = float_to_int
  frame.storage[3] = log
  frame.storage[4] = int_to_str
