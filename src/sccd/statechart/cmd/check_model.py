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
      sc_parser = create_statechart_parser(Globals(), src, load_external=True)

      statechart = parse(src, sc_parser, decorate_exceptions=(ModelError,))

      assert isinstance(statechart, Statechart)
    except Exception as e:
      print(e)