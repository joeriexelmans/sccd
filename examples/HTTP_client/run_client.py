import sys

import client
from sccd.runtime import socket2event

controller = client.Controller(sys.argv[1:])
socket2event.boot_translation_service(controller)
controller.start()
