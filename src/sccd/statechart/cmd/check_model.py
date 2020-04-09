import argparse
import sys
import termcolor
from sccd.statechart.parser.xml import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check if input file(s) is valid statechart model.")
    parser.add_argument('path', metavar='PATH', type=str, help="Model to check.")
    args = parser.parse_args()

    src = args.path

    try:
      path = os.path.dirname(src)
      rules = [("statechart", statechart_parser_rules(Globals(), path, load_external=True))]

      statechart = parse(src, rules, decorate_exceptions=(ModelError,))

      assert isinstance(statechart, Statechart)
    except Exception as e:
      print(e)