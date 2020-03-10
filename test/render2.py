import argparse
import sys
import subprocess
import multiprocessing
from lib.os_tools import *
from sccd.compiler.utils import FormattedWriter
from sccd.runtime.xml_loader2 import *
import lxml.etree as ET

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Render statecharts as SVG images.")
    parser.add_argument('path', metavar='PATH', type=str, nargs='*', help="Models to render. Can be a XML file or a directory. If a directory, it will be recursively scanned for XML files.")
    parser.add_argument('--build-dir', metavar='DIR', type=str, default='build', help="As a first step, input XML files first must be compiled to python files. Directory to store these files. Defaults to 'build'")
    parser.add_argument('--output-dir', metavar='DIR', type=str, default='', help="Directory for SVG rendered output. Defaults to '.' (putting the SVG files with the XML source files)")
    parser.add_argument('--keep-smcat', action='store_true', help="Whether to NOT delete intermediary SMCAT files after producing SVG output. Default = off (delete files)")
    parser.add_argument('--no-svg', action='store_true', help="Don't produce SVG output. This option only makes sense in combination with the --keep-smcat option. Default = off")
    parser.add_argument('--pool-size', metavar='INT', type=int, default=multiprocessing.cpu_count()+1, help="Number of worker processes. Default = CPU count + 1.")
    args = parser.parse_args()

    srcs = get_files(args.path,
      filter=lambda file: (file.startswith("statechart_") or file.startswith("test_")) and file.endswith(".xml"))

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

    def process(src):
      statechart_node = ET.parse(src).getroot()
      tree_node = statechart_node.find(".//tree")
      if tree_node is None:
        return # no tree here :(
      tree = load_state_tree(ModelNamespace(), tree_node)

      target_path = lambda ext: os.path.join(args.output_dir, dropext(src)+ext)
      smcat_target = target_path('.smcat')
      svg_target = target_path('.svg')
      
      make_dirs(smcat_target)

      f = open(smcat_target, 'w')
      w = FormattedWriter(f)

      def name_to_label(name):
        label = name.split('/')[-1]
        return label if len(label) else "root"
      def name_to_name(name):
        return name.replace('/','_')

      # Used for drawing initial state
      class PseudoState:
        def __init__(self, name):
          self.name = name
      # Used for drawing initial state
      class PseudoTransition:
        def __init__(self, source, targets):
          self.source = source
          self.targets = targets
          self.guard = None
          self.trigger = None
          self.actions = []

      transitions = []

      def write_state(s, hide=False):
        if not hide:
          w.write(name_to_name(s.name))
          w.extendWrite(' [label="')
          w.extendWrite(name_to_label(s.name))
          w.extendWrite('"')
          if isinstance(s, ParallelState):
            w.extendWrite(' type=parallel')
          elif isinstance(s, ShallowHistoryState):
            w.extendWrite(' type=history')
          elif isinstance(s, DeepHistoryState):
            w.extendWrite(' type=deephistory')
          else:
            w.extendWrite(' type=regular')
          w.extendWrite(']')
        if s.enter or s.exit:
          w.extendWrite(' :')
          for a in s.enter:
            w.write("onentry/ "+a.render())
          for a in s.exit:
            w.write("onexit/ "+a.render())
          w.write()
        if s.children:
          if not hide:
            w.extendWrite(' {')
            w.indent()
          if s.default_state:
            w.write(name_to_name(s.name)+'_initial [type=initial],')
            transitions.append(PseudoTransition(source=PseudoState(s.name+'/initial'), targets=[s.default_state]))
          for i, c in enumerate(s.children):
            write_state(c)
            w.extendWrite(',' if i < len(s.children)-1 else ';')
          if not hide:
            w.dedent()
            w.write('}')
        transitions.extend(s.transitions)

      write_state(tree.root, hide=True)

      ctr = 0
      for t in transitions:
        label = ""
        if t.trigger:
          label += t.trigger.render()
        if t.guard:
          label += ' ['+t.guard.render()+']'
        if t.actions:
          raises = [a for a in t.actions if isinstance(a, RaiseEvent)]
          label += ','.join([r.render() for r in raises])

        if len(t.targets) == 1:
          w.write(name_to_name(t.source.name) + ' -> ' + name_to_name(t.targets[0].name))
          if label:
            w.extendWrite(': '+label)
          w.extendWrite(';')
        else:
          w.write(name_to_name(t.source.name) + ' -> ' + ']split'+str(ctr))
          if label:
              w.extendWrite(': '+label)
          w.extendWrite(';')
          for tt in t.targets:
            w.write(']split'+str(ctr) + ' -> ' + name_to_name(tt.name))
            w.extendWrite(';')
          ctr += 1

      f.close()
      if args.keep_smcat:
        print("Wrote "+smcat_target)
      if not args.no_svg:
        subprocess.run(["state-machine-cat", smcat_target, "-o", svg_target])
        print("Wrote "+svg_target)
      if not args.keep_smcat:
        os.remove(smcat_target)

    pool_size = min(args.pool_size, len(srcs))
    with multiprocessing.Pool(processes=pool_size) as pool:
      print("Created a pool of %d processes."%pool_size)
      pool.map(process, srcs)
