.PHONY: all clean

SCCDC = python -m sccd.compiler.sccdc
FLAGS = -l python -p eventloop

SOURCES = sccd.xml sccd_performance.xml

TARGET_DIR = target_py
TARGETS = $(TARGET_DIR)/target.py $(TARGET_DIR)/target_performance.py


all: $(TARGET_DIR) $(TARGETS)

clean:
	find $(TARGET_DIR) -type f -delete
	-rmdir $(TARGET_DIR)

$(TARGET_DIR)/target.py: sccd.xml
	$(SCCDC) $(FLAGS) -o $@ $<

$(TARGET_DIR)/target_performance.py: sccd_performance.xml
	$(SCCDC) $(FLAGS) -o $@ $<

$(TARGET_DIR):
	-mkdir $@
	touch $@/__init__.py

