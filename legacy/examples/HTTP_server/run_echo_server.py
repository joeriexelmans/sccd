import sys

import server
from sccd.runtime import socket2event

controller = server.Controller(sys.argv[1:])
socket2event.boot_translation_service(controller)
controller.start()
