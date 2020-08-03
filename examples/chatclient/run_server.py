import threading
import socket
import sys
import io
import collections

BUFFER_SIZE = 1024

if __name__ == "__main__":
    port = int(sys.argv[1])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Thread-safe bidirectional one-to-many mapping between room number and client socket
    class RoomMapping:
        def __init__(self):
            self.client2room = {}
            self.room2clients = collections.defaultdict(set)
            self.lock = threading.Lock()

        def join(self, client, room):
            with self.lock:
                self.room2clients[room].add(client)
                self.client2room[client] = room

        def leave(self, client):
            with self.lock:
                room = self.client2room[client]
                self.room2clients[room].remove(client)
                del self.client2room[client]

        def get_clients_in_same_room(self, client):
            with self.lock:
                room = self.client2room[client]
                return list(self.room2clients[room])

    mapping = RoomMapping()

    def send_line(conn, msg):
        conn.send((msg+"\n").encode('utf-8'))

    def client_thread(conn, address):
        with conn:
            file = conn.makefile();
            for line in file:
                if line.startswith("POLL"):
                    send_line(conn, "ALIVE")

                elif line.startswith("JOIN"):
                    print("JOIN EVENT SERVER " + line)
                    room_number = int(line[5:])
                    mapping.join(conn, room_number)
                    send_line(conn, "ACK JOIN " + str(room_number))
                    # print("joined...", mapping.client2room)

                elif line.startswith("LEAVE"):
                    mapping.leave(conn)
                    send_line(conn, "ACK LEAVE")
                    # print("left...", mapping.client2room)

                elif line.startswith("MSG"):
                    # print("got MSG: ", line)
                    conns = mapping.get_clients_in_same_room(conn)
                    for c in conns:
                        if c is not conn:
                            send_line(c, line)

                else:
                    print("Received line does not match protocol: ", line)
            
        print("Closed client connection: %s:%s" % address)

    with s:
        s.bind(("localhost", port))
        s.listen(5)
        print("Accepting client connections.")

        while True:
            conn, address = s.accept()
            print("Accepted client connection: %s:%s" % address)
            t = threading.Thread(target=client_thread, args=(conn,address))
            t.daemon = True
            t.start()
