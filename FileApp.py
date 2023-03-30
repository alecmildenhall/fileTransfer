#!/usr/bin/env python3.10

from socket import *
import sys
import os
import logging
import threading
import time

## Helper Functions ##

# TODO: change for broadcast table
def stringToTable(string):
    table = []
    string_tables = string.split("/")
    for string_table in string_tables:
        items = string_table.split()
        curr_table = []
        i = 0
        for item in items:
            curr_table.append(item)
            # files list section
            if (i == 5):
                files = []
                string_files = items[5].split("*")
                for string_file in string_files:
                    files.append(string_file)
                if (curr_table[5] == 'none'):
                    curr_table[5] = []
                else:
                    curr_table[5].append(files)
            i = i + 1

        table.append(curr_table)
    
    return table


# TODO: change for broadcast table
def tableToString(table):
    columns = len(table)
    rows = len(table[0])
    output_string = ""

    for i in range(columns):
        row_string = ""
        for j in range(rows):
            if (j < 5):
                row_string = str(table[i][j]) + " "
            # list of files section
            else:
                row_string = ""
                files_string = ""
                flag = 0
                for k in range(len(table[i][j])):
                    files_string = str(table[i][j][k]) + "*"
                    flag = 1
                if (not flag):
                    files_string = "none"
                files_string = files_string.strip("*")
                row_string = row_string + files_string
            output_string = output_string + row_string
        output_string = output_string + "/"
    
    output_string = output_string.strip(" /")
    print("output_string: " + output_string)
    return output_string

# table: [[client_name, client_status, clientIP, client_tcp, client_udp, [file1, file2, etc]], ...]
def updateFiles(name, files, table):
    for client in table:
        if (client[0] == name):
            for file in files:
                if (file not in client[5]):
                    client[5].append(file)
            break

# b_table: [Filename, Owner, Client IP address, Client TCP Port]
def tableToBroadcastTable(table):
    b_table = []
    for client in table:
        owner = client[0]
        client_ip = client[2]
        port = client[3]
        for file in client[5]:
            curr_list = [file, owner, client_ip, port]
            b_table.append(curr_list)
    return b_table

def listenToServer(lock, clientSocket, server_ip, server_port):
    while True:
        message, serverAddress = clientSocket.recvfrom(2048)
        message = message.decode()

        if ():
            # update table
            pass


## Global Variables ##
server_table = []
client_table = []

## Start Main Code ##

if __name__ == "__main__":

    ## Determine Mode ##
    try:
        mode = sys.argv[1]
    except:
        print('use: FileApp -s <port> or \
            use: FileApp -c <name> <server-ip> <server-port> <client-udp-port> <client-tcp-port>')
        sys.exit()

    if (mode == "-s"):
        ## Server Mode ##
        try:
            port = int(sys.argv[2])
        except:
            print('use: FileApp -s <port>')
            sys.exit()

        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind(('', port))

        server_table = []
        # names, online-status, IPaddresses, TCP and UDP port numbers, and filenames

        # receives request
        while True:
            message, clientAddress = serverSocket.recvfrom(2048)
            clientIP = clientAddress[0]
            message = message.decode()
            print("received message: " + message)

            # registration request detected
            if ("reg: " in message):
                message = message[5:]
                print("cleaned message: " + message)

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
                print("server_table: " + str(server_table))
                for client in server_table:
                    if client[0] == client_name:
                        print(client_name + ' is already registered')
                        name_exists = 1
                        break
                
                if (name_exists):
                    message = "error"
                    serverSocket.sendto(message.encode(), clientAddress)
                    continue

                # add client info to table
                server_table.append([client_name, client_status, clientIP, client_tcp, client_udp, []])
                print("updated table: " + str(server_table))

                # send client registered message
                message = "registered"
                serverSocket.sendto(message.encode(), clientAddress)

                # send client updated table
                table_string = tableToString(server_table)
                print("server table: " + table_string)
                serverSocket.sendto(table_string.encode(), clientAddress)

                # check for ACK
                retry = 0
                message, clientAddress = serverSocket.recvfrom(2048)
                message = message.decode()
                if (message == "ACK"):
                    print('ACK received')


                # TODO: if don't receive ACK after 500 ms
                # send table again (try this twice)

                # TODO: broadcast to clients?
                broadcast_table = tableToBroadcastTable(server_table)

            # receive updated files
            elif ('offer' in message):
                # send ACK to client
                ack = "ACK"
                serverSocket.sendto(ack.encode(), clientAddress)

                items = message.split()
                name = items[1]
                files = items[2:]
                print("name: " + str(name))
                print("files: " + str(files))
                print("table: " + str(server_table))

                updateFiles(name, files, server_table)
                print('updated files')
                print('new table: ' + str(server_table))

                # TODO: broadcast to all active clients the most updated list of file offerings
                # - needs threads to accomplish this
                broadcast_table = tableToBroadcastTable(server_table)
                print('broadcast table: ' + str(broadcast_table))
                
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

        print('>>> ', end='', flush=True)

        # send registration request
        status = 'on'
        message = 'reg: ' + name + ' ' + str(client_udp_port) + ' ' + str(client_tcp_port) + ' ' + status
        print("reg req: " + message)
        clientSocket.sendto(message.encode(),(server_ip, server_port))

        # receive registration confirmation
        serverMessage, serverAddress = clientSocket.recvfrom(2048)
        serverMessage = serverMessage.decode()
        print("serverMessage: " + serverMessage)
        if (serverMessage != "registered"):
            print('Error: client is already registered')
            sys.exit()
        
        print('[Welcome, You are registered.]')
        print('>>> ', end='', flush=True)

        # lock creation
        lock = threading.Lock()

        # TODO: thread for listening to the server
        x = threading.Thread(target=listenToServer, args=(lock, clientSocket, server_ip, server_port), daemon=True)

        # TODO: thread for listening to other clients


        # receive updated table
        updated_table_string, serverAddress = clientSocket.recvfrom(2048)

        # once the table is received, client sends ack to server
        # send ACK
        ack = "ACK"
        clientSocket.sendto(ack.encode(),(server_ip, server_port))

        # update table
        updated_table_string = updated_table_string.decode()
        print("updated string: " + updated_table_string)
        client_table = stringToTable(updated_table_string)
        print("client_table: " + str(client_table))
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
                path = os.getcwd() + '/' + dir
                print('path: ' + path)
                if (not os.path.isdir(path)):
                    print('[setdir failed: ' + dir + ' does not exist.]')
                    continue
                
                print('[Successfully set ' + dir + ' as the directory for searching offered files.]')
                setup = True

            elif ("offer" in command):
                if (not setup):
                    print('Error: must set a directory first')
                    continue
                inputs = command.split()
                if (len(inputs) < 2):
                    print('use: offer <filename1> ...')
                    continue
                files = inputs[1:]

                # send server UDP message with updated files
                message = 'offer ' + name + ' '
                file_string = ''
                for file in files:
                    file_string = file_string + ' ' + file
                message = message + file_string
                message = message.strip()
                clientSocket.sendto(message.encode(),(server_ip, server_port))

                # TODO: wait for ACK from server
                serverMessage, serverAddress = clientSocket.recvfrom(2048)
                serverMessage = serverMessage.decode()
                if (serverMessage == "ACK"):
                    print('[Offer Message received by Server.]')
                else:
                    # TODO: change
                    print('[No ACK from Server, please try again later.]')
                # timeout at 500ms
                # retry 2x
            else:
                print("Error: unsupported command")
                continue


    else:
        print('use: FileApp -s <port> or \
            use: FileApp -c <name> <server-ip> <server-port> <client-udp-port> <client-tcp-port>')
        sys.exit()
