## test.py

The Python program `test.py` replaces the old `run_tests.py`. It takes test input files (in SCCD XML format) as parameter. It compiles tests and runs them.

For example, to run the "semantics" tests:
```
python3 test.py semantics
```
This will create a 'build' directory with compiled statechart models. It is safe to remove this directory after testing, but this directory serves as a 'cache' for build artifacts.

## render.py

The Python program `render.py` renders SVG graphs for test files. Rendered SVG files are checked in to this repository. If you wish to re-render them, you need the NPM (NodeJS) package 'state-machine-cat'. Install NodeJS and NPM, and then install the NPM package 'state-machine-cat':
```
npm i -g state-machine-cat
```
You can now render all the tests in the 'semantics' dir:
```
python3 render.py semantics
```
By default, the SVG files are stored next to the test XML files.