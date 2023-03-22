#!/usr/bin/env python3.10

from socket import *
import sys

## Registration ##

# only registered clients should be able to offer files
#   and receive the updated list of files shared by other registered clients
# not all clients need to register files
# server takes in registration requests from clients using the UDP protocol
#   - server needs to be started before the clients can start coming online

# server has to maintain a table (nick-names of clients + files they are sharing + their IP addresses + port numbers)

try:
    mode = sys.argv[1]
except:
    print('use: FileApp -s <port> or \
          use: FileApp -c <name> <server-ip> <server-port> <client-udp-port> <client-tcp-port>')
    sys.exit()

if (mode == "-s"):
    # server mode
    table = []
    # names, online-status, IPaddresses, TCP and UDP port numbers, and filenames

    # recieves registration request
elif (mode == "-c"):
    # client mode

    # get command line arguments
    try:
        name = sys.argv[2]
        server_ip = sys.argv[3]
        server_port = sys.argv[4]
        client_udp_port = sys.argv[5]
        client_tcp_port = sys.argv[6]
    except:
        print('use: FileApp -c <name> <server-ip> <server-port> <client-udp-port> <client-tcp-port>')
        sys.exit()

    # check arguments
    try:
        socket.inet_aton(server_ip)
    except:
        print('invalid IP address')
        sys.exit()
    
    if ((int(server_port) < 1024 or int(server_port) > 65535) or 
        (int(client_udp_port) < 1024 or int(client_udp_port) > 65535) or
        (int(client_tcp_port) < 1024 or int(client_tcp_port) > 65535)):
        print('given port(s) out of range')
        sys.exit()

    # initiate client communication to server
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    # send registration request


    # sucessful client registration?
    # TODO: do i need prompt first? what makes this successful
    print('>>> [Welcome, You are registered.]')

    local_table = []
    # name of offered files, client name, IP, TCP port number
    # update (overwrite) its local table when the server sends information 
    # about all the other clients. Once the table is received, the client 
    # should send an ack to the server.

    updated = False
    if (updated):
        print('>>> [Client table updated.]')

else:
    print('use: FileApp -s <port> or \
          use: FileApp -c <name> <server-ip> <server-port> <client-udp-port> <client-tcp-port>')
    sys.exit()
