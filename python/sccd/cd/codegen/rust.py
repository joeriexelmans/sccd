
class ClassDiagramRustGenerator:

    def __init__(self, writer):
        self.w = writer

    def visit_SingleInstanceCD(self, cd):
        from sccd.statechart.codegen.rust import StatechartRustGenerator
        gen = StatechartRustGenerator(self.w, cd.globals)
        cd.statechart.accept(gen)
