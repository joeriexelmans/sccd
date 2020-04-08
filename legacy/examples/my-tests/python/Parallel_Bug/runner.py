import sys
sys.path.append("../")

import tester
import threading
from sccd.runtime.statecharts_core import Event
import time

controller = tester.Controller(keep_running=False)

try:
    controller.start()
except KeyboardInterrupt:
    pass
