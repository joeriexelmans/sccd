import argparse
import sys
import subprocess
import os
from sccd.util.os_tools import *
from sccd.util.indenting_writer import *
from sccd.statechart.parser.xml import *
from sccd.statechart.static import priority

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Render the priorities between transitions in a statechart as a graph.")
    parser.add_argument('path', metavar='PATH', type=str, nargs='*', help="Models to render. Can be a XML file or a directory. If a directory, it will be recursively scanned for XML files.")
    args = parser.parse_args()

    srcs = get_files(args.path,
      filter=lambda file: (file.startswith("statechart_") or file.startswith("test_") or file.startswith("model_")) and file.endswith(".xml"))

    if len(srcs) == 0:
      print("No input files specified.")
      print()
      parser.print_usage()
      exit()

    try:
        subprocess.run(["dot", "-?"], capture_output=True)
    except:
        print("Could not run command 'dot'. Make sure GraphViz dot is installed.")

    for src in srcs:
        path = os.path.dirname(src)
        parse_sc = statechart_parser_rules(Globals(), path, load_external=False)

        def find_statechart(el):
          def when_done(statechart):
            return statechart
          # When parsing <test>, only look for <statechart> node in it.
          # All other nodes will be ignored.
          return ({"statechart": parse_sc}, when_done)

        statechart = parse_f(src, {
          "test": find_statechart,
          "single_instance_cd": find_statechart,
          "statechart": parse_sc,
        }, ignore_unmatched=True)

        assert isinstance(statechart, Statechart)

        if statechart.semantics.has_multiple_variants():
          print("Skipping statechart from " + src + ". Statechart has multiple semantic variants.")
          continue

        tree = statechart.tree

        dot_target = dropext(src)+'_priorities.dot'
        svg_target = dropext(src)+'_priorities.svg'

        with open(dot_target, 'w') as f:
            w = IndentingWriter(f)
            w.write("digraph priorities {")
            w.indent()

            graph = priority.get_graph(tree, statechart.semantics)

            print("Priority graph has", len(graph), "edges")

            def label(t):
                return '"'+str(tree.transition_list.index(t)) + ". " + t.source.short_name + "->" + t.target.short_name+'"'

            for high, low in graph:
                w.write(label(high) + " -> " + label(low) + ";")

            w.dedent()
            w.write("}")

        subprocess.run(["dot", "-Tsvg", dot_target, "-o", svg_target])
        print("Wrote", svg_target)
        os.remove(dot_target)
