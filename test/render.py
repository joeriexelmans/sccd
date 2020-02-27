import argparse
import sys
import subprocess
from lib.os_tools import *
from lib.builder import *
from sccd.compiler.utils import FormattedWriter
from sccd.runtime.statecharts_core import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Render statecharts as SVG images.")
    parser.add_argument('path', metavar='PATH', type=str, nargs='*', help="Models to render. Can be a XML file or a directory. If a directory, it will be recursively scanned for XML files.")
    parser.add_argument('--build-dir', metavar='DIR', type=str, default='build', help="Directory for built tests. Defaults to 'build'")
    parser.add_argument('--render-dir', metavar='DIR', type=str, default='.', help="Directory for SVG rendered output. Defaults to '.' (putting the SVG files with the XML source files)")
    args = parser.parse_args()

    try:
      subprocess.run(["state-machine-cat", "-h"], capture_output=True)
    except:
        print("Failed to run 'state-machine-cat'. Make sure this application is installed on your system.")
        exit()

    builder = Builder(args.build_dir)
    render_builder = Builder(args.render_dir)
    srcs = get_files(args.path, filter=xml_filter)

    for src in srcs:
      module = builder.build_and_load(src)
      model = module.Model()

      for class_name, _class in model.classes.items():
        target = render_builder.target_file(src, '_'+class_name+'.smcat')
        svg_target = render_builder.target_file(src, '_'+class_name+'.svg')
        
        make_dirs(target)

        f = open(target, 'w')
        w = FormattedWriter(f)
        sc = _class().statechart

        def name_to_label(name):
          label = name.split('/')[-1]
          return label if len(label) else "root"
        def name_to_name(name):
          return name.replace('/','_')
        class PseudoState:
          def __init__(self, name):
            self.name = name
        class PseudoTransition:
          def __init__(self, source, targets):
            self.source = source
            self.targets = targets
            self.trigger = None

        transitions = []

        def write_state(s, hide=False):
          if not hide:
            w.write(name_to_name(s.name))
            w.extendWrite(' [label="')
            w.extendWrite(name_to_label(s.name))
            w.extendWrite('"')
            if isinstance(s, ParallelState):
              w.extendWrite(' type=parallel')
            elif isinstance(s, HistoryState):
              w.extendWrite(' type=history')
            elif isinstance(s, DeepHistoryState):
              w.extendWrite(' type=deephistory')
            else:
              w.extendWrite(' type=regular')
            w.extendWrite(']')
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

        write_state(sc.root, hide=True)

        ctr = 0
        for t in transitions:
          label = ""
          if t.trigger and t.trigger.name:
              label = (t.trigger.port + '.' if t.trigger.port else '') + t.trigger.name

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
        subprocess.run(["state-machine-cat", target, "-o", svg_target])
        os.remove(target)
        print("Rendered "+svg_target)
