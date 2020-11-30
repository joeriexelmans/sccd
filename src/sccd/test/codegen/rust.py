from sccd.test.static.syntax import *
from sccd.statechart.codegen.rust import compile_statechart
from sccd.util.indenting_writer import *

import os
import sccd.cd.codegen
rustlib = os.path.dirname(sccd.cd.codegen.__file__) + "/sccdlib.rs"

def compile_test(variants: List[TestVariant], w: IndentingWriter):

    with open(rustlib, 'r') as file:
        data = file.read()
        w.writeln(data)

    if len(variants) > 0:
        cd = variants[0].cd
        compile_statechart(cd.get_default_class(), cd.globals, w)


    w.writeln("fn main() {")
    w.indent()

    for v in variants:
        w.writeln("// Test variant")
        w.writeln("let mut controller: Controller<Event> = Default::default();")
        w.writeln("let mut sc: Statechart = Default::default();")
        for i in v.input:
            if len(i.events) > 1:
                raise Exception("Multiple simultaneous input events not supported")
            elif len(i.events) == 0:
                raise Exception("Test declares empty bag of input events - not supported")

            w.writeln("controller.add_input(Entry::<Event>{")
            w.writeln("  timestamp: %d," % i.timestamp.opt)
            w.writeln("  event: Event::%s," % i.events[0].name)
            w.writeln("  target: Target::Narrowcast(&mut sc),")
            w.writeln("});")

        w.writeln("controller.run_until(Until::Eternity);")
        pass

    w.dedent()
    w.writeln("}")