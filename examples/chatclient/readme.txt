Chat client demo
================

What's this?
------------

- A chat client, modeled as a statechart interacting with native Python code (in 'lib').

- A matching chat server, ad-hoc implemented in small python script.

Specification of the client's behavior can be found here:

http://msdl.cs.mcgill.ca/people/hv/teaching/MoSIS/assignments/Statecharts


Running
-------

To start the server:

  python3 run_server.py 9000

where '9000' is the desired listening port.

To launch the client (in another terminal):

  python3 run_client.py

The client has two servers hardcoded to which it will attempt to connect in round-robin fashion:
  localhost:9000
  localhost:9001

Launch multiple clients to test the "chat" functionality :)

Doesn't matter which is launched first: client or server. Try to stop a server (Ctrl+C, SIGINT) with connected clients and see how the clients detect a lost connetion. Re-launch the server and watch them re-connect (and re-join the room they were in, thank God for history states!).

Hint: Set the environment variable SCCDDEBUG=1 to get insight into the transitions and steps being made.