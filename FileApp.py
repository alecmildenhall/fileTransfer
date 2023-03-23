#!/usr/bin/env python3.10

from socket import *
import sys

## Helper Functions ##

# TODO: something is going wrong here bc the last thing is [] rn, just make it a string for now buddy
def stringToTable(string):
    table = []
    string_tables = string.split("/")
    for string_table in string_tables:
        items = string_table.split()
        curr_table = []
        for item in items:
            curr_table.append(item)
        table.append(curr_table)
    
    return table


def tableToString(table):
    columns = len(table)
    rows = len(table[0])
    output_string = ""

    for i in range(columns):
        for j in range(rows):
            print("table[i][j] = " + str(table[i][j]))
            output_string = str(table[i][j]) + " "
        output_string = output_string + "/"
    
    output_string = output_string.strip(" /")
    return output_string

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
        clientIP = clientAddress[0]
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
        # TODO: change files --> some list of lists or sm
        table.append([client_name, client_status, clientIP, client_tcp, client_udp, "files"])

        # send client registered message
        message = "registered"
        serverSocket.sendto(message.encode(), clientAddress)

        # send client updated table
        table_string = tableToString(table)
        serverSocket.sendto(table_string.encode(), clientAddress)

        # check for ACK
        message, clientAddress = serverSocket.recvfrom(2048)
        message = message.decode()
        if (message == "ack"):
            print('ACK received')


        # if don't receive ACK after 500 ms
        # send table again (try this twice)


elif (mode == "-c"):
    # client mode

    # get command line arguments
    try:
        name = sys.argv[2]
        server_ip = sys.argv[3]
        server_port = int(sys.argv[4])
        client_udp_port = int(sys.argv[5])
        client_tcp_port = int(sys.argv[6])
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
    message = name + ' ' + str(client_udp_port) + ' ' + str(client_tcp_port) + ' ' + status
    clientSocket.sendto(message.encode(),(server_ip, server_port))

    # receive registration confirmation
    while True:
        serverMessage, serverAddress = clientSocket.recvfrom(2048)
        serverMessage = serverMessage.decode()
        if (serverMessage == "registered"):
            break
    
    print('>>> [Welcome, You are registered.]')

    # receive updated table
    updated_table_string, serverAddress = clientSocket.recvfrom(2048)

    # send ACK
    ack = "ACK"
    clientSocket.sendto(ack.encode(),(server_ip, server_port))

    # update table
    updated_table_string = updated_table_string.decode()
    updated_table = stringToTable(updated_table_string)
    print('>>> [Client table updated.]')

    
    # name of offered files, client name, IP, TCP port number
    # update (overwrite) its local table when the server sends information 
    # about all the other clients. Once the table is received, the client 
    # should send an ack to the server.


else:
    print('use: FileApp -s <port> or \
          use: FileApp -c <name> <server-ip> <server-port> <client-udp-port> <client-tcp-port>')
    sys.exit()
