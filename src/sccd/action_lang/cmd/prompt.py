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
  print("Enter statements or expressions. Most statements end with ';'. Statements will be executed, expressions will be evaluated. Either can have side effects.")
  print("Examples:")
  print("  basic stuff:")
  print("    greeting = \"hello\";")
  print("    to_whom = \" world\";")
  print("    greeting + to_whom")
  print("  more interesting: higher order functions:")
  print("    apply = func(i: int, f: func(int) -> int) { return f(i); } ;")
  print("    apply(10, func(i: int) { return i+1; })")
  print()

  while True:
    try:
      line = input("> ")
      try:
        # Attempt to parse as a statement
        stmt = parse_block(line) # may raise LarkError
        stmt.init_stmt(scope)

        # Grow current stack frame if necessary
        diff = scope.size() - len(memory.current_frame().storage)
        if diff > 0:
          memory.current_frame().storage.extend([None]*diff)

        stmt.exec(memory)
      except LarkError as e:
        try:
          # Attempt to parse as an expression
          expr = parse_expression(line)
          expr_type = expr.init_expr(scope)
          val = expr.eval(memory)
          print("%s: %s" % (str(val), str(expr_type)))
        except LarkError:
          raise e

    except (UnexpectedToken, UnexpectedCharacters) as e:
      print(" " + " "*e.column + "^")
      print(type(e).__name__+":", e)
    except (LarkError, ModelError, SCCDRuntimeException) as e:
      print(type(e).__name__+":", e)
    except (KeyboardInterrupt, EOFError):
      print()
      exit()