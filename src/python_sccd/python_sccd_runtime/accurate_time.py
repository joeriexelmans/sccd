import time as t
import os

global start_time
def set_start_time():
    global start_time
    start_time = t.time()

if os.name == 'posix':
    def time():
        return int((t.time() - start_time) * 1000)
elif os.name == 'nt':
    def time():
        return int(t.clock() * 1000)
