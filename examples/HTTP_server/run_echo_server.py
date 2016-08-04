import sys

import server
import socket2event

controller = server.Controller(sys.argv[1:])
socket2event.boot_translation_service(controller)
controller.start()