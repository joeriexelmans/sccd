import argparse
import sys
import subprocess
import multiprocessing
import os
from sccd.util.os_tools import *
from sccd.util.indenting_writer import *
from sccd.statechart.parser.xml import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Render statecharts as SVG images.")
    parser.add_argument('path', metavar='PATH', type=str, nargs='*', help="Models to render. Can be a XML file or a directory. If a directory, it will be recursively scanned for XML files.")
    parser.add_argument('--output-dir', metavar='DIR', type=str, default='.', help="Directory for SVG rendered output. Defaults to '.' (putting the SVG files with the XML source files)")
    parser.add_argument('--keep-smcat', action='store_true', help="Whether to NOT delete intermediary SMCAT files after producing SVG output. Default = off (delete files)")
    parser.add_argument('--no-svg', action='store_true', help="Don't produce SVG output. This option only makes sense in combination with the --keep-smcat option. Default = off")
    parser.add_argument('--pool-size', metavar='INT', type=int, default=multiprocessing.cpu_count()+1, help="Number of worker processes. Default = CPU count + 1.")
    args = parser.parse_args()

    srcs = get_files(args.path,
      filter=lambda file: (file.startswith("statechart_") or file.startswith("test_") or file.startswith("model_")) and file.endswith(".xml"))

    if len(srcs):
      if not args.no_svg:
        try:
          subprocess.run(["state-machine-cat", "-h"], capture_output=True)
        except:
            print("Failed to run 'state-machine-cat'. Make sure this application is installed on your system.")
            exit()
    else:
      print("No input files specified.")
      print()
      parser.print_usage()
      exit()

    # From this point on, disable terminal colors as we write output files
    os.environ["ANSI_COLORS_DISABLED"] = "1"

    def process(src):
      try:
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

        root = statechart.tree.root

        target_path = lambda ext: os.path.join(args.output_dir, dropext(src)+ext)
        smcat_target = target_path('.smcat')
        svg_target = target_path('.svg')
        
        make_dirs(smcat_target)

        f = open(smcat_target, 'w')
        w = IndentingWriter(f)

        def name_to_label(state):
          label = state.full_name.split('/')[-1]
          if state.stable:
            label += " ✓"
          return label if len(label) else "root"
        def name_to_name(name):
          return name.replace('/','_')

        # Used for drawing initial state
        class PseudoState:
          @dataclass
          class Opt:
            full_name: str
          def __init__(self, name):
            self.stable = False
            self.opt = PseudoState.Opt(name)
        # Used for drawing initial state
        class PseudoTransition:
          def __init__(self, source, target):
            self.source = source
            self.target = target
            self.guard = None
            self.trigger = None
            self.actions = []

        transitions = []

        def write_state(s, hide=False):
          if not hide:
            w.writeln(name_to_name(s.full_name))
            w.write(' [label="')
            w.write(name_to_label(s))
            w.write('"')
            if isinstance(s.type, AndState):
              w.write(' type=parallel')
            elif isinstance(s, ShallowHistoryState):
              w.write(' type=history')
            elif isinstance(s, DeepHistoryState):
              w.write(' type=deephistory')
            else:
              w.write(' type=regular')
            w.write(']')
          if s.enter or s.exit:
            w.write(' :')
            for a in s.enter:
              w.writeln("enter "+a.render())
            for a in s.exit:
              w.writeln("exit "+a.render())
            w.writeln()
          if s.children:
            if not hide:
              w.write(' {')
              w.indent()
            if s.default_state:
              w.writeln(name_to_name(s.full_name)+'_initial [type=initial],')
              transitions.append(PseudoTransition(source=PseudoState(s.full_name+'/initial'), target=s.default_state))
            s.children.reverse() # this appears to put orthogonal components in the right order :)
            for i, c in enumerate(s.children):
              write_state(c)
              w.write(',' if i < len(s.children)-1 else ';')
            if not hide:
              w.dedent()
              w.writeln('}')
          transitions.extend(s.transitions)

        write_state(root, hide=True)

        ctr = 0
        for t in transitions:
          label = ""
          if t.trigger:
            label += t.trigger.render()
          if t.guard:
            label += ' ['+t.guard.render()+']'
          if t.actions:
            label += ' '.join(a.render() for a in t.actions)

          w.writeln(name_to_name(t.source.full_name) + ' -> ' + name_to_name(t.target.full_name))
          if label:
            w.write(': '+label)
          w.write(';')

        f.close()
        if args.keep_smcat:
          print("Wrote "+smcat_target)
        if not args.no_svg:
          subprocess.run(["state-machine-cat", smcat_target, "-o", svg_target])
          print("Wrote "+svg_target)
        if not args.keep_smcat:
          os.remove(smcat_target)
      
      except SkipFile:
        # Raised for test files that have their statechart defined in an external file.
        # We skip these files because we parse that external file already directly.
        # print("Skip", src)
        pass
      except Exception as e:
        import traceback
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)

    pool_size = min(args.pool_size, len(srcs))
    with multiprocessing.Pool(processes=pool_size) as pool:
      print("Created a pool of %d processes."%pool_size)
      pool.map(process, srcs)
