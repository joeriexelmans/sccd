from sccd.action_lang.static.expression import *
from sccd.util.debug import *

# Builtin "global" functions in statechart language

BuiltIn = Scope("builtin", None)

# The way we add our builtin functions is a bit hackish because they are implemented
# "natively" in Python, rather than in action language code.

BuiltIn.declare("INSTATE", SCCDFunction([SCCDArray(SCCDString)], SCCDBool), const=True)

def load_builtins(memory: MemoryInterface, execution):
  import math
  import termcolor
  
  memory.push_frame(BuiltIn)

  # Wrapper functions of the signature expected by the action language:

  def in_state(memory: MemoryInterface, state_list: List[str]) -> bool:
    return execution.in_state(state_list)

  # Manually write wrapper functions to memory:

  frame = memory.current_frame()

  frame.storage[0] = in_state
