# README

Required libraries and modules:
- Python 3.9.12 used
- socket, threading, sys, os, logging, and time modules used
- no other external libraries used/installed

How To Run:
1. First start the server from the command line with:
python FileApp.py -s <port>

Where <port> is the port number of the server.

ex: python FileApp.py -s 1024

2. Start a client from the command line with:
FileApp -c <name> <server-ip> <server-port> \ <client-udp-port> <client-tcp-port>

Where <name> refers to the name you want to assign to the client. (The other arguments are self described.) Multiple client instances can be started with multiple terminals.

ex: python FileApp.py -c client1 127.0.0.1 1024 2000 2001
