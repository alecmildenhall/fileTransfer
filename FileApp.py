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
server_started = False

try:
    mode = sys.argv[1]
except:
    print('use: FileApp -s <port> or \
          use: FileApp -c <name> <server-ip> <server-port> <client-udp-port> <client-tcp-port>')
    sys.exit()

if (mode == "-s"):
    # server mode
    try:
        port = sys.argv[2]
    except:
        print('use: FileApp -s <port>')
        sys.exit()

    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', port))
    serverSocket.listen(3) # Accepts 3 sequential connections

    table = []
    # names, online-status, IPaddresses, TCP and UDP port numbers, and filenames

    server_started = True

    # receives registration request
    message, clientAddress = serverSocket.recvfrom(2048)

    try:
        client_info = message.split()
        client_name = client_info[0]
        client_udp = client_info[1]
        client_tcp = client_info[2]
        client_status = client_info[3]
    except:
        print('invalid registration request')
        sys.exit() # TODO: this is prob not the right thing to do
    
    # check if name already exists
    for client in table:
        if client[0] == client_name:
            print(client_name + ' is already registered')
            # TODO: send error message and reject registration

    # add client info to table
    table.append([client_name, client_status, clientAddress, client_tcp, client_udp, []])


elif (mode == "-c"):
    # client mode
    if (not server_started):
        print('server must be started first')
        sys.exit()

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
    status = 'on'
    message = name + ' ' + client_udp_port + ' ' + client_tcp_port + ' ' + status
    clientSocket.sendto(message,(server_ip, server_port))

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
