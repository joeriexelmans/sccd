.PHONY: all clean

SCCDC = python -m sccd.compiler.sccdc
FLAGS = -l python -p eventloop
FLAGS_THREADS = -l python -p threads

TARGET_DIR = target_py
TARGETS = $(TARGET_DIR)/target.py $(TARGET_DIR)/multiwindow.py $(TARGET_DIR)/target_performance.py $(TARGET_DIR)/target_performance_threads.py $(TARGET_DIR)/target_performance_cpu_time.py


all: $(TARGET_DIR) $(TARGETS)

clean:
	find $(TARGET_DIR) -type f -delete
	-rmdir $(TARGET_DIR)

$(TARGET_DIR)/target.py: sccd.xml
	$(SCCDC) $(FLAGS) -o $@ $<

$(TARGET_DIR)/multiwindow.py: sccd_multiwindow.xml
	$(SCCDC) $(FLAGS) -o $@ $<

$(TARGET_DIR)/target_performance.py: sccd_performance.xml
	$(SCCDC) $(FLAGS) -o $@ $<

$(TARGET_DIR)/target_performance_threads.py: sccd_performance_threads.xml
	$(SCCDC) $(FLAGS_THREADS) -o $@ $<

$(TARGET_DIR)/target_performance_cpu_time.py: sccd_performance_cpu_time.xml
	$(SCCDC) $(FLAGS_THREADS) -o $@ $<

$(TARGET_DIR):
	-mkdir $@
	touch $@/__init__.py

