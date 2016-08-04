.PHONY: all clean

SCCDC = python -m sccd.compiler.sccdc
FLAGS = -l python -p eventloop

SOURCES = ai_controller.xml player_controller.xml
TARGETS = ai_controller.py player_controller.py
PY_BYPRODUCTS = $(TARGETS:%.py=%.pyc)

all: $(TARGETS)

clean:
	rm -f $(TARGETS) $(PY_BYPRODUCTS)

%.py: %.xml
	$(SCCDC) $(FLAGS) -o $@ $<

