Compiler
========
To compile a conforming SCCDXML file, the provided Python compiler can be used. The compiler can compile conforming SCCD models to two languages: Python and Javascript. Three platforms are supported, for more information see :ref:`runtime_platforms`.

The compiler can be used from the command line as follows::

    $python -m sccd.compiler.sccdc --help
    usage: python -m sccd.compiler.sccdc [-h] [-o OUTPUT] [-v VERBOSE]
                                         [-p PLATFORM] [-l LANGUAGE]
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
                            Let the compiled code run on top of threads, gameloop
                            or eventloop. The default is eventloop.
      -l LANGUAGE, --language LANGUAGE
                            Target language, either "javascript" or "python".
                            Defaults to the latter.