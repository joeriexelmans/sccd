.PHONY: all all_javascript all_python clean clean_javascript clean_python test test_javascript test_python help

SCCDC = python -m sccd.compiler.sccdc

PYTHON = python
BROWSER = firefox 2>/dev/null -new-window

JS_FLAGS = -l javascript -p eventloop
PY_FLAGS = -l python -p threads

JS_EXT = js
PY_EXT = py

SRC_DIR = src
TARGET_DIR_PREFIX = target_
JS_TARGET_DIR = $(TARGET_DIR_PREFIX)js
PY_TARGET_DIR = $(TARGET_DIR_PREFIX)py


#SOURCES = after.xml associate_event.xml correct_duplicate_state_id.xml enter_exit_hierarchy.xml guard.xml history_deep.xml history_parallel_deep.xml history.xml inner_first.xml instate.xml multiple_target.xml object_manager.xml outer_first.xml parallel_history_2.xml parallel_history.xml parallel.xml

SRC_SUBDIRS = $(shell ls $(SRC_DIR))
JS_TARGET_SUBDIRS = $(SRC_SUBDIRS:%=$(JS_TARGET_DIR)/%)
PY_TARGET_SUBDIRS = $(SRC_SUBDIRS:%=$(PY_TARGET_DIR)/%)
PY_MODULES = $(PY_TARGET_DIR)/__init__.py $(PY_TARGET_SUBDIRS:%=%/__init__.py)

SOURCES = $(shell find src -type f -name *\.xml)

#SOURCES_JS = inheritance_js.xml # javascript-only tests
#SOURCES_PY = #inheritance_py.xml # python-only tests

JS_TARGETS = $(SOURCES:$(SRC_DIR)/%.xml=$(JS_TARGET_DIR)/%.js) $(SOURCES_JS:$(SRC_DIR)/%.xml=$(JS_TARGET_DIR)/%.js)

PY_TARGETS = $(SOURCES:$(SRC_DIR)/%.xml=$(PY_TARGET_DIR)/%.py) $(SOURCES_PY:$(SRC_DIR)/%.xml=$(PY_TARGET_DIR)/%.py)

PY_BYPRODUCTS = $(PY_TARGETS:%.py=%.pyc) $(PY_MODULES:%.py=%.pyc)

##
##Target             Description
##

all:              ## Build all tests.
all: all_javascript all_python

all_javascript:   ## Build Javascript tests.
all_javascript: $(JS_TARGET_SUBDIRS) $(JS_TARGETS) $(JS_ONLY_TARGETS)

all_python:       ## Build Python tests.
all_python: $(PY_TARGET_SUBDIRS) $(PY_TARGETS) $(PY_ONLY_TARGETS) $(PY_MODULES)

clean:            ## Remove all build artifacts.
clean: clean_javascript clean_python

clean_javascript: ## Remove Javascript build artifacts.
	-rm -f  $(JS_TARGETS) $(JS_ONLY_TARGETS)
	-rmdir $(JS_TARGET_SUBDIRS) $(JS_TARGET_DIR)

clean_python:     ## Remove Python build artifacts.
	-rm -f  $(PY_TARGETS) $(PY_ONLY_TARGETS) $(PY_BYPRODUCTS) $(PY_MODULES)
	-rmdir $(PY_TARGET_SUBDIRS) $(PY_TARGET_DIR)

test:             ## Run all tests.
test: test_javascript test_python

test_javascript:  ## Run Javascript tests. This will cause a browser window to open.
test_javascript: all_javascript run_tests.html
	$(BROWSER) run_tests.html &

test_python:      ## Run Python tests.
test_python: all_python run_tests.py
	$(PYTHON) run_tests.py

$(JS_TARGET_DIR)/%.js :: $(SRC_DIR)/%.xml
	$(SCCDC) $(JS_FLAGS) -o $@ $<

$(PY_TARGET_DIR)/%.py :: $(SRC_DIR)/%.xml
	$(SCCDC) $(PY_FLAGS) -o $@ $<

$(JS_TARGET_DIR) $(PY_TARGET_DIR):
	-mkdir $@

$(PY_TARGET_SUBDIRS): $(PY_TARGET_DIR)
	-mkdir $@

$(JS_TARGET_SUBDIRS): $(JS_TARGET_DIR)
	-mkdir $@

$(PY_MODULES):
	touch $@

help:             ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

##
