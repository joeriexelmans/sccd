import sys
import readline
import termcolor
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
      stmt = parse_block(line)
      stmt.init_stmt(scope)
      print_debug(termcolor.colored(str(stmt), 'yellow'))

      # Grow current stack frame if necessary
      diff = scope.size() - len(memory.current_frame().storage)
      if diff > 0:
        memory.current_frame().storage.extend([None]*diff)

      if isinstance(stmt, ExpressionStatement):
        expr_type = stmt.expr.init_expr(scope) # expr already initialized but init_expr should be idempotent
        val = stmt.expr.eval(memory)
        print("%s: %s" % (str(val), str(expr_type)))
      else:
        stmt.exec(memory)

    except (UnexpectedToken, UnexpectedCharacters) as e:
      print(" " + " "*e.column + "^")
      print(e)
    except (LarkError, ModelError, SCCDRuntimeException) as e:
      print(e)
    except KeyboardInterrupt:
      print()
      exit()