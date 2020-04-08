.PHONY: all clean

SCCDC = python -m sccd.compiler.sccdc
FLAGS = -l python -p threads

SOURCE = sccd.xml

TARGET_DIR = target_py
TARGET = $(TARGET_DIR)/target.py


all: $(TARGET_DIR) $(TARGET)

clean:
	find $(TARGET_DIR) -type f -delete
	-rmdir $(TARGET_DIR)

$(TARGET): $(SOURCE)
	$(SCCDC) $(FLAGS) -o $@ $<

$(TARGET_DIR):
	-mkdir $@
	touch $@/__init__.py

