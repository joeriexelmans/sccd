import threading
from python_runtime.statecharts_core import Event
import socket

def _recv(controller, sock):
    data = sock.recv(4096)
    controller.addInput(Event("received_socket", "socket_in", [sock, data]), 0.0)

def _accept(controller, sock):
    conn, addr = sock.accept()
    controller.addInput(Event("accepted_socket", "socket_in", [sock, conn]), 0.0)

def _connect(controller, sock, destination):
    sock.connect(destination)
    controller.addInput(Event("connected_socket", "socket_in", [sock]), 0.0)

def _create(controller, _):
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    controller.addInput(Event("created_socket", "socket_in", [sock]), 0.0)

def _send(controller, sock, data):
    sent = sock.send(data)
    controller.addInput(Event("sent_socket", "socket_in", [sock, sent]), 0.0)

def _close(controller, sock):
    sock.close()
    controller.addInput(Event("closed_socket", "socket_in", [sock]), 0.0)

def _bind(controller, sock, addr):
    sock.bind(addr)
    controller.addInput(Event("bound_socket", "socket_in", [sock]), 0.0)

def _listen(controller, sock):
    sock.listen(1)
    controller.addInput(Event("listened_socket", "socket_in", [sock]), 0.0)

def _wrapper_func(*args):
    func = args[0]
    controller = args[1]
    sock = args[2]
    try:
        func(*args[1:])
    except socket.error as e:
        print("ERROR " + str(e))
        controller.addInput(Event("error_socket", "socket_in", [sock, e]), 0.0)
    except Exception as e:
        print("UNKNOWN ERROR " + str(e))
        controller.addInput(Event("unknown_error_socket", "socket_in", [sock, e]), 0.0)

def _start_on_daemon_thread(func, args):
    new_args = [func]
    new_args.extend(args)
    args = new_args
    thrd = threading.Thread(target=_wrapper_func, args=args)
    thrd.daemon = True
    thrd.start()

def boot_translation_service(controller):
    _start_on_daemon_thread(_poll, [controller, None])

def _poll(controller, _):
    socket_out = controller.addOutputListener("socket_out")
    while 1:
            evt = socket_out.fetch(-1)
            name, params = evt.getName(), evt.getParameters()
            print("Got event " + str(evt))
            if name == "accept_socket":
                _start_on_daemon_thread(_accept, [controller, params[0]])
            elif name == "recv_socket":
                _start_on_daemon_thread(_recv, [controller, params[0]])
            elif name == "connect_socket":
                _start_on_daemon_thread(_connect, [controller, params[0], params[1]])
            elif name == "create_socket":
                _start_on_daemon_thread(_create, [controller, None])
            elif name == "close_socket":
                _start_on_daemon_thread(_close, [controller, params[0]])
            elif name == "send_socket":
                _start_on_daemon_thread(_send, [controller, params[0], params[1]])
            elif name == "bind_socket":
                _start_on_daemon_thread(_bind, [controller, params[0], params[1]])
            elif name == "listen_socket":
                _start_on_daemon_thread(_listen, [controller, params[0]])
            elif name == "stop":
                break