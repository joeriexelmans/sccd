from sccd.test.static.syntax import *
from sccd.util.indenting_writer import *
from sccd.cd.codegen.rust import ClassDiagramRustGenerator
from sccd.statechart.codegen.rust import ident_event_type

class TestRustGenerator(ClassDiagramRustGenerator):
    def __init__(self, w):
        super().__init__(w)

    def visit_TestVariant(self, variant):
        variant.cd.accept(self)

        self.w.writeln("pub fn run() {")
        self.w.indent()

        self.w.writeln("use sccd::controller;")
        self.w.writeln("use sccd::statechart;")
        self.w.writeln("use sccd::statechart::SC;")
        self.w.writeln("use sccd::statechart::Scheduler;")
        if DEBUG:
            self.w.writeln("debug_print_sizes::<controller::TimerId>();")
        self.w.writeln();

        self.w.writeln("let mut raised = Vec::<statechart::OutEvent>::new();")
        self.w.writeln("let mut output = |out: statechart::OutEvent| {")
        if DEBUG:
            self.w.writeln("  eprintln!(\"^{}:{}\", out.port, out.event);")
        self.w.writeln("  raised.push(out);")
        self.w.writeln("};")
        self.w.writeln("let mut controller = controller::Controller::<InEvent>::new();")
        self.w.writeln("let mut sc: Statechart::<controller::TimerId> = Default::default();")
        self.w.writeln("sc.init(&mut controller, &mut output);")
        for i in variant.input:
            if len(i.events) > 1:
                raise UnsupportedFeature("Multiple simultaneous input events not supported")
            elif len(i.events) == 0:
                raise UnsupportedFeature("Test declares empty bag of input events")
            self.w.writeln("controller.set_timeout(%d, InEvent::%s);" % (i.timestamp.opt, ident_event_type(i.events[0].name)))

        self.w.writeln("controller.run_until(&mut sc, controller::Until::Eternity, &mut output);")
        self.w.writeln("assert_eq!(raised, [%s]);" % ", ".join('statechart::OutEvent{port:"%s", event:"%s"}' % (e.port, e.name) for o in variant.output for e in o))

        self.w.dedent()
        self.w.writeln("}")

    def visit_Test(self, test):
        for i, v in enumerate(test.variants):
            self.w.writeln("mod variant%d {" % i)
            self.w.indent()
            v.accept(self)
            self.w.dedent()
            self.w.writeln("}")
            self.w.writeln()

        self.w.writeln("fn main() {")

        for i, v in enumerate(test.variants):
            self.w.writeln("  eprintln!(\"Test variant %d\");" % i)
            self.w.writeln("  variant%d::run();" % i)
            self.w.writeln("  eprintln!(\"Passed.\");")
        self.w.writeln("}")
        self.w.writeln()
