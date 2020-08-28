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

        try:
            statechart = parse_f(src, {
              "test": find_statechart,
              "single_instance_cd": find_statechart,
              "statechart": parse_sc,
            }, ignore_unmatched=True)
        except SkipFile:
            continue

        assert isinstance(statechart, Statechart)

        if statechart.semantics.has_multiple_variants():
          print("Skipping statechart from " + src + ". Statechart has multiple semantic variants.")
          continue

        tree = statechart.tree
        semantics = statechart.semantics

        hierarchical = {
            HierarchicalPriority.NONE: priority.none,
            HierarchicalPriority.SOURCE_PARENT: priority.source_parent,
            HierarchicalPriority.SOURCE_CHILD: priority.source_child,
            HierarchicalPriority.ARENA_PARENT: priority.arena_parent,
            HierarchicalPriority.ARENA_CHILD: priority.arena_child,
        }[semantics.hierarchical_priority]

        same_state = {
            SameSourcePriority.NONE: priority.none,
            SameSourcePriority.EXPLICIT: priority.explicit_same_state,
        }[semantics.same_source_priority]

        orthogonal = {
            OrthogonalPriority.NONE: priority.none,
            OrthogonalPriority.EXPLICIT: priority.explicit_ortho,
        }[semantics.orthogonal_priority]

        same_state_edges = same_state(tree)
        hierarchical_edges = hierarchical(tree)
        orthogonal_edges = orthogonal(tree)

        dot_target = dropext(src)+'_priorities.dot'
        svg_target = dropext(src)+'_priorities.svg'

        with open(dot_target, 'w') as f:
            w = IndentingWriter(f)
            w.write("digraph priorities {")
            w.indent()

            pseudo_dict = {}

            def node_label(t):
                if isinstance(t, priority.PseudoVertex):
                    try:
                        label = pseudo_dict[t]
                    except KeyError:
                        pseudo_dict[t] = label = "pseudo"+str(len(pseudo_dict))
                        w.write("%s [label=\"\" shape=circle style=filled fixedsize=true width=0.4 height=0.4 fillcolor=\"grey\"];" % label)
                    return label
                elif isinstance(t, Transition):
                    return '"'+str(tree.transition_list.index(t)) + ". " + t.source.short_name + "->" + t.target.short_name+'"'
            def draw_edges(edges, color):
                for high, low in edges:
                    w.write("%s -> %s [color=%s];" % (node_label(high), node_label(low), color))

            draw_edges(same_state_edges, "green")
            draw_edges(hierarchical_edges, "red")
            draw_edges(orthogonal_edges, "blue")

            w.dedent()
            w.write("}")

        subprocess.run(["dot", "-Tsvg", dot_target, "-o", svg_target])
        print("Wrote", svg_target)
        os.remove(dot_target)
