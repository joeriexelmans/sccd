# Statecharts and Class Diagram Compiler

## Dependencies

### Mandatory

* CPython >= 3.6 or PyPy >= 7.3.0 (Compatible with Python 3.6)
* The following packages from PyPi:
  * [lark-parser](https://github.com/lark-parser/lark) for parsing state references and action code
  * [lxml](https://lxml.de/) for parsing the SCCD XML input format
  * [termcolor](https://pypi.org/project/termcolor/) for colored terminal output
  * [dataclasses](https://pypi.org/project/dataclasses/) (not needed for Python >= 3.7)

### Optional

* [state-machine-cat](https://github.com/sverweij/state-machine-cat) to render statecharts as SVG images. Runs on NodeJS, installable from NPM.