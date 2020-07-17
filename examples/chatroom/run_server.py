import chatserver
import socket2event
import sys

if len(sys.argv) != 2:
    print("Usage:")
    print("  %s port" % sys.argv[0])
    sys.exit(1)

controller = chatserver.Controller(int(sys.argv[1]))
socket2event.boot_translation_service(controller)
controller.start()

try:
    import time
    while 1:
        time.sleep(1)
finally:
    controller.stop()
