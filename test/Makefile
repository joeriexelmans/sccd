.PHONY: all all_javascript all_python clean clean_javascript clean_python test test_javascript test_python help

SCCDC = python3 -m sccd.compiler.sccdc

PYTHON = python3
BROWSER = firefox 2>/dev/null -new-window

JS_FLAGS = -l javascript -p eventloop
PY_FLAGS = -l python -p threads

SRC_DIRS = semantics
BUILD_DIR = build

SOURCES = $(shell find $(SRC_DIRS) -type f -name *\.xml)

JS_TARGETS = $(addprefix $(BUILD_DIR)/, $(SOURCES:%.xml=%.js))
PY_TARGETS = $(addprefix $(BUILD_DIR)/, $(SOURCES:%.xml=%.py))

all:              ## Build all tests.
all: all_javascript all_python

all_javascript:   ## Build Javascript tests.
all_javascript: $(JS_TARGETS) $(JS_TARGETS) $(JS_ONLY_TARGETS)

all_python:       ## Build Python tests.
all_python: $(PY_TARGETS)

clean:            ## Remove all build artifacts.
clean:
	rm -rf $(BUILD_DIR)

test:             ## Run all tests.
test: test_javascript test_python

test_javascript:  ## Run Javascript tests. This will cause a browser window to open.
test_javascript: all_javascript run_tests.html
	$(BROWSER) run_tests.html &

test_python:      ## Run Python tests.
test_python: all_python run_tests.py
	$(PYTHON) run_tests.py

$(BUILD_DIR)/%.py : %.xml
	mkdir -p $(dir $@)
	-$(SCCDC) $(PY_FLAGS) -o $@ $<

$(BUILD_DIR)/%.js : %.xml
	mkdir -p $(dir $@)
	-$(SCCDC) $(JS_FLAGS) -o $@ $<

help:             ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

##
