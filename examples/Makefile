.PHONY: all

SUB_DIRS = $(shell ls .)

all:
	for D in $(SUB_DIRS); do $(MAKE) -C $$D $@ ; done

clean:
	for D in $(SUB_DIRS); do $(MAKE) -C $$D $@ ; done
