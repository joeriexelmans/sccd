.PHONY: all clean

SCCDC = python -m sccd.compiler.sccdc
FLAGS = -l python -p threads

SOURCE = client.xml
TARGET = client.py

all: $(TARGET)

clean:
	find . -type f -name '$(TARGET)*' -delete

$(TARGET): $(SOURCE)
	$(SCCDC) $(FLAGS) -o $@ $<

