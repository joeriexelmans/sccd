Statecharts and Class Diagram Compiler
======================================

Usage
-------------
Manual for the compiler written in Python :
```sh
$python sccdc.py --help
usage: sccdc.py [-h] [-o OUTPUT] [-v VERBOSE] [-p PLATFORM] [-l LANGUAGE]
                input

positional arguments:
  input                 The path to the XML file to be compiled.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        The path to the generated code. Defaults to the same
                        name as the input file but with matching extension.
  -v VERBOSE, --verbose VERBOSE
                        2 = all output; 1 = only warnings and errors; 0 = only
                        errors; -1 = no output. Defaults to 2.
  -p PLATFORM, --platform PLATFORM
                        Let the compiled code run on top of threads, eventloop or
                        gameloop. The default is threads.
  -l LANGUAGE, --language LANGUAGE
                        Target language, "python" or "javascript". Defaults
                        to "python".
```

Tests
-------------
Building tests can be done by executing `make clean all` in the `tests` folder. Executing the tests written for the Python compiler and generated Python code can be done by running `run_tests.py`. This file imports the test cases from the `tests/target_py` folder. Javascript tests are run using the `run_tests.html` file.