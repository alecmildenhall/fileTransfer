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
#server_started = False

try:
    mode = sys.argv[1]
except:
    print('use: FileApp -s <port> or \
          use: FileApp -c <name> <server-ip> <server-port> <client-udp-port> <client-tcp-port>')
    sys.exit()

if (mode == "-s"):
    # server mode
    try:
        port = int(sys.argv[2])
    except:
        print('use: FileApp -s <port>')
        sys.exit()

    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', port))

    table = []
    # names, online-status, IPaddresses, TCP and UDP port numbers, and filenames

    # receives registration request
    while True:
        message, clientAddress = serverSocket.recvfrom(2048)
        message = message.decode()

        try:
            client_info = message.split()
            client_name = client_info[0]
            client_udp = client_info[1]
            client_tcp = client_info[2]
            client_status = client_info[3]
        except:
            print('invalid registration request')
            continue
        
        # check if name already exists
        name_exists = 0
        for client in table:
            if client[0] == client_name:
                print(client_name + ' is already registered')
                name_exists = 1
                break
        
        if (name_exists):
            continue

        # add client info to table
        table.append([client_name, client_status, clientAddress, client_tcp, client_udp, []])

        # send client registered message
        message = "registered"
        serverSocket.sendto(message.encode(), clientAddress)

        # send client updated table
        


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
    for c in server_ip:
        if (c != '.' and not str(c).isdigit()):
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
    clientSocket.sendto(message.encode(),(server_ip, server_port))

    # receive registration confirmation
    while True:
        serverMessage, serverAddress = clientSocket.recvfrom(2048)
        serverMessage = serverMessage.decode()
        if (serverMessage == "registered"):
            break
    
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
