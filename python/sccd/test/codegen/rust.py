from sccd.test.static.syntax import *
from sccd.util.indenting_writer import *
from sccd.cd.codegen.rust import ClassDiagramRustGenerator
from sccd.action_lang.codegen.rust import UnsupportedFeature
from sccd.statechart.codegen.rust import *

class TestRustGenerator(ClassDiagramRustGenerator):
    def __init__(self, w):
        super().__init__(w)

    def visit_TestVariant(self, variant):
        variant.cd.accept(self)

        self.w.writeln("pub fn run_test() {")
        self.w.indent()

        self.w.writeln("use sccd::controller::*;")
        self.w.writeln("use sccd::statechart;")
        self.w.writeln("use sccd::statechart::SC;")
        self.w.writeln("use sccd::statechart::Scheduler;")
        if DEBUG:
            self.w.writeln("debug_print_sizes::<Controller<InEvent>>();")
        self.w.writeln();

        self.w.writeln("// Setup ...")
        self.w.writeln("let mut raised = Vec::<OutEvent>::new();")
        self.w.writeln("let mut output = |out: OutEvent| {")
        self.w.writeln("  raised.push(out);")
        self.w.writeln("};")
        self.w.writeln("let mut controller = Controller::<InEvent>::default();")
        self.w.writeln("let mut sc = Statechart::<Controller::<InEvent>>::default();")
        self.w.writeln()
        self.w.writeln("// Initialize statechart (execute actions of entering default states)")
        self.w.writeln("sc.init(&mut controller, &mut output);")
        self.w.writeln()
        self.w.writeln("// Add test input")
        for i in variant.input:
            if len(i.events) > 1:
                raise UnsupportedFeature("Multiple simultaneous input events not supported")
            elif len(i.events) == 0:
                raise UnsupportedFeature("Test declares empty bag of input events")

            # Convert python value to rust literal
            # Should find a better solution ...
            def to_rust_literal(value):
                if isinstance(value, int):
                    return str(value)
                elif isinstance(value, str):
                    return '"%s"' % value
                else:
                    raise Exception("Incomplete implementation")

            self.w.write("controller.set_timeout(%d, InEvent::%s(%s));" % (i.timestamp.opt, ident_event_enum_variant(i.events[0].name), ", ".join(to_rust_literal(p) for p in i.events[0].params)))
        self.w.writeln()

        self.w.writeln("// Run simulation, as-fast-as-possible")
        self.w.writeln("controller.run_until(&mut sc, Until::Eternity, &mut output);")
        self.w.writeln()
        self.w.writeln("// Check if output is correct")
        self.w.writeln("assert_eq!(raised, [%s]);" % ", ".join("OutEvent::%s(%s)" % (ident_event_enum_variant(e.name), ", ".join(to_rust_literal(p) for p in e.params)) for o in variant.output for e in o))

        self.w.dedent()
        self.w.writeln("}")

    def visit_Test(self, test):
        for i, v in enumerate(test.variants):
            self.w.writeln("mod variant%d {" % (i+1))
            self.w.indent()
            v.accept(self)
            self.w.dedent()
            self.w.writeln("}")
            self.w.writeln()

        self.w.writeln("fn main() {")

        for i, v in enumerate(test.variants):
            self.w.writeln("  eprintln!();")
            self.w.writeln("  eprintln!(\"Test variant %d of %d\");" % (i+1, len(test.variants)))
            self.w.writeln("  variant%d::run_test();" % (i+1))
            self.w.writeln("  eprintln!(\"Passed.\");")
        self.w.writeln("}")
        self.w.writeln()
