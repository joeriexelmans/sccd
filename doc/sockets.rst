Socket Communication
====================

Sockets, for network communication, are an oftenly needed capability for many complex system.
By default, however, Statecharts, and SCCD in particular, do not handle socket communication at all.
Shifting all socket communication into action code is not an option either, as it is potentially a blocking operation.
Additionally, the code wraps different socket implementations and socket configuration.

This module will, after starting the translation service, translate all events on the *socket_in* and *socket_out* port to socket operations.
Blocking then happens on another thread, while the statechart can continue its usual execution.
When the socket operation returns, the result will be raised in the statechart as an event.

Initialization
--------------

To use the translation service, several steps should be followed:

    1. Import sccd.sccd_runtime.socket2event as socket2event;
    2. Write your model with a *socket_in* and *socket_out* port;
    3. Before starting the controller, invoke *socket2event.boot_translation_service(controller)* with the controller as its first argument;
    4. Now raise and catch events as specified here, to communicate with sockets.

Input Events
------------

+-------------------+-----------------------------------+-------------------------------+
| Event             | Parameters                        | Meaning                       |
+===================+===================================+===============================+
| accept_socket     | socket                            | socket.accept()               |
+-------------------+-----------------------------------+-------------------------------+
| recv_socket       | socket                            | socket.recv(2**16)            |
+-------------------+-----------------------------------+-------------------------------+
| connect_socket    | socket, address                   | socket.connect(address)       |
+-------------------+-----------------------------------+-------------------------------+
| create_socket     |                                   | new Socket()                  |
+-------------------+-----------------------------------+-------------------------------+
| close_socket      | socket                            | socket.close()                |
+-------------------+-----------------------------------+-------------------------------+
| send_socket       | socket, data                      | socket.send(data)             |
+-------------------+-----------------------------------+-------------------------------+
| bind_socket       | socket, address                   | socket.bind(address)          |
+-------------------+-----------------------------------+-------------------------------+
| listen_socket     | socket                            | socket.listen()               |
+-------------------+-----------------------------------+-------------------------------+
| stop              | socket                            | stops translator service      |
+-------------------+-----------------------------------+-------------------------------+

Output Events
-------------

+-----------------------+-----------------------------------+-------------------------------+
| Event                 | Arguments                         | Response to                   |
+=======================+===================================+===============================+
| received_socket       | socket, data                      | recv_socket                   |
+-----------------------+-----------------------------------+-------------------------------+
| sent_socket           | socket, bytes                     | send_socket                   |
+-----------------------+-----------------------------------+-------------------------------+
| accepted_socket       | socket, connection                | accept_socket                 |
+-----------------------+-----------------------------------+-------------------------------+
| connected_socket      | socket                            | connect_socket                |
+-----------------------+-----------------------------------+-------------------------------+
| closed_socket         | socket                            | close_socket                  |
+-----------------------+-----------------------------------+-------------------------------+
| bound_socket          | socket                            | bind_socket                   |
+-----------------------+-----------------------------------+-------------------------------+
| listened_socket       | socket                            | listen_socket                 |
+-----------------------+-----------------------------------+-------------------------------+
| error_socket          | socket, error                     | Socket error occurs           |
+-----------------------+-----------------------------------+-------------------------------+
| unknown_error_socket  | socket, error                     | Python error occurs           |
+-----------------------+-----------------------------------+-------------------------------+

HTTP client/server
------------------

Using this library, an HTTP echo client and server are implemented.
The server echoes all data received from the client.
The client connects to the server and sends some data.
These are included in the examples directory

Compile the server using::

   python python_sccd_compiler/sccdc.py -p threads server.xml

and the client using::

   python python_sccd_compiler/sccdc.py -p threads client.xml

Afterwards, you can run the server as::

   python run_server.py

which will start up a simple HTTP echo server on port 8080
(configurable in constructor).
Then you can start up several clients using::

   python run_client.py

The client will send out a counter to the server and print out the
reply. The server is able to connect to multiple clients simultaneously,
so can handle multiple open connections without getting confused.
