import time as t
import os

global start_time
start_time = None

if os.name == 'posix':
    def time():
        global start_time
        if start_time is None:
            start_time = t.time()
        return t.time() - start_time
elif os.name == 'nt':
    def time():
        return t.clock()
