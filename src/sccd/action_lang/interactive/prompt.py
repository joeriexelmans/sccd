import sys
import readline
from sccd.action_lang.dynamic.memory import *
from sccd.action_lang.parser.text import *
from lark.exceptions import *

if __name__ == "__main__":
  scope = Scope("interactive", parent=None)
  memory = Memory()
  memory.push_frame(scope)
  readline.set_history_length(1000)

  while True:
    try:
      line = input("> ")
      stmt = parse_stmt(line)
      stmt.init_stmt(scope)

      # Grow current stack frame if necessary
      diff = scope.size() - len(memory.current_frame().storage)
      if diff > 0:
        memory.current_frame().storage.extend([None]*diff)

      if isinstance(stmt, ExpressionStatement):
        val = stmt.expr.eval(memory)
        print(val)
      else:
        stmt.exec(memory)

    except (LarkError, ModelError, SCCDRuntimeException) as e:
      print(e)
    except KeyboardInterrupt:
      print()
      exit()