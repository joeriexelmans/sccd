import sys

class IndentingWriter:
    def __init__(self, spaces=2, out=sys.stdout, initial=0):
        self.spaces = spaces
        self.out = out
        self.state = initial
        self.newline = True

    def indent(self):
        self.state += self.spaces

    def dedent(self):
        self.state -= self.spaces

    def writeln(self, s=""):
        if self.newline:
            self.out.write(' '*self.state)
        self.out.write(s + '\n')
        self.newline = True

    def write(self, s=""):
        if self.newline:
            self.out.write(' '*self.state)
        self.out.write(s)
        self.newline = False
