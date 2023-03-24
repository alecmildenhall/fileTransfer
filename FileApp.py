#!/usr/bin/env python3.10

from socket import *
import sys
import os

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
            # files list section
            if (item == 5):
                files = []
                string_files = items[5].split("*")
                for string_file in string_files:
                    files.append(string_file)
            curr_table[5].append(files)

        table.append(curr_table)
    
    return table


# TODO: edit this so last item (5th) is a list
def tableToString(table):
    columns = len(table)
    rows = len(table[0])
    output_string = ""

    for i in range(columns):
        for j in range(rows):
            print("table[i][j] = " + str(table[i][j]))
            output_string = str(table[i][j]) + " "
            # list of files section
            if (j == 5):
                for k in range(len(table[i][j])):
                    output_string = str(table[i][j][k]) + "*"
                output_string = output_string.strip("*")
        output_string = output_string + "/"
    
    output_string = output_string.strip(" /")
    return output_string

# TODO: match name & add files
# table: [client_name, client_status, clientIP, client_tcp, client_udp, "files"]
def updateFiles(name, files, table):
    for client in table:
        if (table[client][0] == name):
            for file in files:
                if (file not in table[client][5]):
                    table[client][5].append(file)
            break

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
        table.append([client_name, client_status, clientIP, client_tcp, client_udp, []])

        # send client registered message
        message = "registered"
        serverSocket.sendto(message.encode(), clientAddress)

        # send client updated table
        table_string = tableToString(table)
        serverSocket.sendto(table_string.encode(), clientAddress)

        # check for ACK
        retry = 0
        message, clientAddress = serverSocket.recvfrom(2048)
        message = message.decode()
        if (message == "ACK"):
            print('ACK received')


        # TODO: if don't receive ACK after 500 ms
        # send table again (try this twice)

        # receive updated files
        message, clientAddress = serverSocket.recvfrom(2048)
        message = message.decode()
        if ('offer' in message):
            items = message.split()
            name = items[1]
            files = items[2:]
            # TODO: match name & add files
            updateFiles(name, files, table)


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

    print('>>> ', end='', flush=True)

    # initiate client communication to server
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    # send registration request
    status = 'on'
    message = name + ' ' + str(client_udp_port) + ' ' + str(client_tcp_port) + ' ' + status
    clientSocket.sendto(message.encode(),(server_ip, server_port))

    # receive registration confirmation
    while True:
        try:
            serverMessage, serverAddress = clientSocket.recvfrom(2048)
            serverMessage = serverMessage.decode()
            if (serverMessage == "registered"):
                break
        except:
            print('registration error')
    
    print('[Welcome, You are registered.]')
    print('>>> ', end='', flush=True)

    # receive updated table
    updated_table_string, serverAddress = clientSocket.recvfrom(2048)

    # once the table is received, client sends ack to server
    # send ACK
    ack = "ACK"
    clientSocket.sendto(ack.encode(),(server_ip, server_port))

    # update table
    updated_table_string = updated_table_string.decode()
    updated_table = stringToTable(updated_table_string)
    print('[Client table updated.]')

    setup = False
    while True:
        command = input('>>> ')

        # setdir functionality
        if ("setdir" in command):
            inputs = command.split()
            if (len(inputs) != 2):
                print('use: setdir <dir>')
                continue
    
            dir = inputs[1]

            # search for directory
            path = os.getcwd()
            print('path: ' + path)
            if (not os.path.isdir(path)):
                print('[setdir failed: <dir> does not exist.]')
                continue
            
            print('[Successfully set <dir> as the directory for searching offered files.]')
            setup = True

        # TODO: offer functionality
        elif ("offer" in command):
            if (not setup):
                print('must set a directory first')
                continue
            inputs = command.split()
            if (len(inputs) < 2):
                print('use: offer <filename1> ...')
                continue
            files = inputs[1:]

            # send server UDP message with updated files
            message = 'offer ' + name + ' '
            for file in files:
                message = file + ' '
            message = message.strip()
            clientSocket.sendto(message.encode(),(server_ip, server_port))


else:
    print('use: FileApp -s <port> or \
          use: FileApp -c <name> <server-ip> <server-port> <client-udp-port> <client-tcp-port>')
    sys.exit()
