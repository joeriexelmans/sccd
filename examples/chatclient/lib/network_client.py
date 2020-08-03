import threading
import socket
import sys
import io
import queue
from dataclasses import dataclass
from typing import *

SERVERS = [ "localhost:9000", "localhost:9001" ]

# returns the number of hardcoded servers of the client
def get_nr_of_servers():
    return len(SERVERS)

# gets the information of the server with the index provided
def get_server(i):
    return SERVERS[i]

from sccd.action_lang.static.types import *

SCCD_EXPORTS = {
    "get_nr_of_servers": (get_nr_of_servers, SCCDFunction([], SCCDInt)),
    "get_server": (get_server, SCCDFunction([SCCDInt], SCCDString)),
}


from sccd.controller.controller import *
from sccd.realtime.eventloop import *

class NetworkClient:
    def __init__(self, eventloop: ThreadSafeEventLoop):
        self.eventloop = eventloop
        self.queue = queue.Queue() # output events from the statechart (for us to handle) are added to this queue
        self.recv_thread = None

    # Starts the network client in a new thread.
    # Networking stuff must run in its own thread, because socket IO is blocking.
    def start(self):
        def event_handler_thread():
            while True:
                name, params = self.queue.get()

                if name == "connect":
                    address = params[0]
                    host, port = address.split(':')
                    port = int(port)
                    # print("NetworkClient: attempting to connect...")
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect((host, port))

                        def recv_thread():
                            file = sock.makefile()
                            for line in file:
                                if line.startswith("ACK JOIN"):
                                    self.eventloop.add_input_now_threadsafe("network", "joined")
                                elif line.startswith("ACK LEAVE"):
                                    self.eventloop.add_input_now_threadsafe("network", "left")
                                elif line.startswith("MSG"):
                                    msg = line[4:]
                                    self.eventloop.add_input_now_threadsafe("network", "receive_message", [msg])
                                elif line.startswith("ALIVE"):
                                    self.eventloop.add_input_now_threadsafe("network", "alive")

                        self.recv_thread = threading.Thread(target=recv_thread)
                        self.recv_thread.daemon = True
                        self.recv_thread.start()
                        # print("NetworkClient: connected: started recv_thread")

                        self.eventloop.add_input_now_threadsafe("network", "connected")
                    except ConnectionError:
                        pass


                elif name == "disconnect":
                    sock.close()

                    # print("NetworkClient: waiting for recv_thread...")
                    self.recv_thread.join()
                    self.recv_thread = None
                    # print("NetworkClient: recv_thread is done.")

                    self.eventloop.add_input_now_threadsafe("network", "disconnected")

                elif name == "join":
                    sock.send(("JOIN " + str(params[0]) + "\n").encode('utf-8'))

                elif name == "leave":
                    sock.send("LEAVE\n".encode('utf-8'))

                elif name == "poll":
                    sock.send("POLL\n".encode('utf-8'))

                elif name == "send_message":
                    sock.send(("MSG " + str(params[0]) + "\n").encode('utf-8'))


        t = threading.Thread(target=event_handler_thread)
        t.daemon = True
        t.start()

    def add_input(self, name, params):
        self.queue.put((name, params))
