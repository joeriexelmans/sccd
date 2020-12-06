import threading
import subprocess
import tempfile
import os
from unittest import SkipTest
from typing import *
from sccd.test.static.syntax import TestVariant
from sccd.statechart.codegen.rust import UnsupportedFeature
from sccd.test.codegen.rust import compile_test
from sccd.util.indenting_writer import IndentingWriter
from sccd.util.debug import *

# Generate Rust code from the test case. This Rust code is piped to a Rust compiler (rustc) process, which reads from stdin. The Rust compiler outputs a binary in a temp dir. We then run the created binary as a subprocess.
# If the result code of either the Rust compiler or the created binary is not 0 ("success"), the 'unittest' fails.
def run_variants(variants: List[TestVariant], unittest):
    if DEBUG:
        stdout = None
        stderr = None
    else:
        stdout = subprocess.DEVNULL
        stderr = subprocess.STDOUT

    output_file = os.path.join(tempfile.gettempdir(), "sccd_rust_out")
    print_debug("Writing binary to " + output_file)

    with subprocess.Popen(["rustc", "-o", output_file, "-"],
        stdin=subprocess.PIPE,
        stdout=stdout,
        stderr=subprocess.PIPE) as pipe:

        class PipeWriter:
            def __init__(self, pipe):
                self.pipe = pipe
            def write(self, s):
                self.pipe.stdin.write(s.encode(encoding='UTF-8'))

        w = IndentingWriter(out=PipeWriter(pipe))

        try:
            compile_test(variants, w)
        except UnsupportedFeature as e:
            raise SkipTest("unsupported feature: " + str(e))

        pipe.stdin.close()

        print_debug("Generated Rust code.")

        ruststderr = pipe.stderr.read().decode('UTF-8')

        status = pipe.wait()

        if DEBUG:
            print(ruststderr)

        if status != 0:
            # This does not indicate a test failure, but an error in our code generator
            raise Exception("Rust compiler status %d. Sterr:\n%s" % (status, ruststderr))

    print_debug("Generated binary. Running...")

    with subprocess.Popen([output_file],
        stdout=stdout,
        stderr=subprocess.PIPE) as binary:

        binarystderr = binary.stderr.read().decode('UTF-8')

        status = binary.wait()

        if status != 0:
            unittest.fail("Test status %d. Stderr:\n%s" % (status, binarystderr))
