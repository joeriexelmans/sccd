import os

DEBUG = os.environ['SCCDDEBUG']
def print_debug(msg):
    if DEBUG:
        print(msg)
