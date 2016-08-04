.PHONY: all clean

SCCDC = python ../../../python_sccd_compiler/sccdc.py
FLAGS = -l python -p eventloop

SOURCE = sccd.xml

TARGET_DIR = target_py
TARGET = $(TARGET_DIR)/sccd.py


all: $(TARGET_DIR) $(TARGET)

clean:
	-rm -f  $(TARGET)
	-rmdir $(TARGET_DIR)

$(TARGET): $(SOURCE)
	$(SCCDC) $(FLAGS) -o $@ $<

$(TARGET_DIR):
	-mkdir $@

