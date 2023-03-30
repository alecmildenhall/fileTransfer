#!/usr/bin/env python3.10

from socket import *
import sys
import os
import logging
import threading
import time

## Helper Functions ##

# string: filename owner ip port / ...
def stringToTable(string):
    table = []
    string_tables = string.split("/")
    for string_table in string_tables:
        curr_table = []
        items = string_table.split()    
        for item in items:
            curr_table.append(item)
        table.append(curr_table)
    #print("table from string: " + str(table))
    return table


# table: [[filename, owner, client ip address, port], ...]
def tableToString(table):
    output_string = ""

    for file in table:
        for item in file:
            output_string = output_string + str(item) + " "
        output_string = output_string.strip(" ")
        output_string = output_string + "/"
    output_string = output_string.strip("/")

    #print("output_string: " + output_string)
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

def listenToServer(lock, forServerSocket, server_ip, server_port):
    while True:
        message, serverAddress = forServerSocket.recvfrom(2048)
        message = message.decode()

        if ("update: " in message):
            # receive updated table
            message = message[8:]
            #print("cleaned message: " + str(message))

            # once the table is received, client sends ack to server
            # send ACK
            ack = "ACK"
            forServerSocket.sendto(ack.encode(),(server_ip, server_port))

            # update client table
            with lock:
                global client_table
                client_table = stringToTable(message)

            #print("client_table: " + str(client_table))
            with lock:
                print('[Client table updated.]')
                print('>>> ', end='', flush=True)

        # TODO: change
        # timeout at 500ms
        # retry 2x
        elif (message == "ACK"):
            with lock:
                print('[Offer Message received by Server.]')
                print('>>> ', end='', flush=True)

        else:
            with lock:
                print('[No ACK from Server, please try again later.]')
                print('>>> ', end='', flush=True)

def listenToClient(lock, forClientsSocket):
    while True:
        # accept client
        connectionSocket, addr = forClientsSocket.accept() ## RETURNS CONNECTION SOCKET
        print('< Accepting connection request from ' + str(addr[0]) + '>')
        print("addr: " + str(addr))

        # receive file request
        message = connectionSocket.recv(2048)
        message = message.decode()
        items = message.split()
        filename = items[0]
        clientname = items[1]

        # transfer file
        with open(filename, "rb") as f:
            i = 0
            while True:
                bytes_read = f.read(4096)
                if not bytes_read:
                    break
                forClientsSocket.sendall(bytes_read)
                if (i == 0):
                    print('< Transferring ' + filename + ' >')
                i = i + 1

        # finish transferring file
        print('< ' + filename + ' transferred successfully! >')

        # close connection
        connectionSocket.close()
        print('< Connection with ' + clientname + ' closed. >')


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

        # receives request
        while True:
            message, clientAddress = serverSocket.recvfrom(2048)
            clientIP = clientAddress[0]
            message = message.decode()
            #print("received message: " + message)

            # registration request detected
            if ("reg: " in message):
                message = message[5:]
                #print("cleaned message: " + message)

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
                #print("server_table: " + str(server_table))
                for client in server_table:
                    if client[0] == client_name:
                        #print('Error: ' + client_name + ' is already registered')
                        name_exists = 1
                        break
                
                if (name_exists):
                    message = "error"
                    serverSocket.sendto(message.encode(), clientAddress)
                    continue

                # add client info to table
                server_table.append([client_name, client_status, clientIP, client_tcp, client_udp, []])
                #print("updated server table: " + str(server_table))

                # send client registered message
                message = "registered"
                serverSocket.sendto(message.encode(), clientAddress)

                # send clients updated table
                broadcast_table = tableToBroadcastTable(server_table)
                #print("broadcast table: " + str(broadcast_table))
                table_string = tableToString(broadcast_table)
                #print("server table: " + table_string)
                message = "update: " + table_string

                for client in server_table:
                    if (client[1] == 'on'):
                        curr_clientAddress = (client[2], int(client[4]))
                        serverSocket.sendto(message.encode(), curr_clientAddress)

                # check for ACK
                retry = 0
                message, clientAddress = serverSocket.recvfrom(2048)
                message = message.decode()
                if (message == "ACK"):
                    print('ACK received')


                # TODO: if don't receive ACK after 500 ms
                # send table again (try this twice)

            # receive updated files
            elif ('offer' in message):
                # send ACK to client
                ack = "ACK"
                serverSocket.sendto(ack.encode(), clientAddress)

                items = message.split()
                name = items[1]
                files = items[2:]
                #print("name: " + str(name))
                #print("files: " + str(files))
                #print("table: " + str(server_table))

                updateFiles(name, files, server_table)
                #print('updated files')
                #print('new table: ' + str(server_table))

                # TODO: broadcast to all active clients the most updated list of file offerings
                # - needs threads to accomplish this
                broadcast_table = tableToBroadcastTable(server_table)
                table_string = tableToString(broadcast_table)
                message = "update: " + table_string

                for client in server_table:
                    if (client[1] == 'on'):
                        curr_clientAddress = (client[2], int(client[4]))
                        serverSocket.sendto(message.encode(), curr_clientAddress)
                
    elif (mode == "-c"):
        ## Client Mode ##

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

        # create client socket for server (UDP)
        forServerSocket = socket(AF_INET, SOCK_DGRAM)
        forServerSocket.bind(('', client_udp_port))

        # create socket for other clients (TCP)
        forClientsSocket = socket(AF_INET,SOCK_STREAM)
        forClientsSocket.bind(('', client_tcp_port))
        forClientsSocket.listen(3)

        #print('>>> ', end='', flush=True)

        # send registration request
        status = 'on'
        message = 'reg: ' + name + ' ' + str(client_udp_port) + ' ' + str(client_tcp_port) + ' ' + status
        #print("reg req: " + message)
        forServerSocket.sendto(message.encode(),(server_ip, server_port))

        # receive registration confirmation
        serverMessage, serverAddress = forServerSocket.recvfrom(2048)
        serverMessage = serverMessage.decode()
        #print("serverMessage: " + serverMessage)
        if (serverMessage != "registered"):
            print('Error: client is already registered')
            sys.exit()
        
        print('>>> [Welcome, You are registered.]')

        # lock creation
        lock = threading.Lock()

        # thread for listening to the server
        x = threading.Thread(target=listenToServer, args=(lock, forServerSocket, server_ip, server_port), daemon=True)
        x.start()
        #print('>>> ', end='', flush=True)
        #print("after thread")

        # TODO: thread for listening to other clients
        y = threading.Thread(target=listenToClient, args=(lock, forClientsSocket), daemon=True)
        y.start()

        ## UI ##
        setup = False
        while True:
            command = input('>>> ')

            path = ""
            # setdir functionality
            if ("setdir" in command):
                inputs = command.split()
                if (len(inputs) != 2):
                    print('use: setdir <dir>')
                    continue
        
                dir = inputs[1]

                # search for directory
                path = os.getcwd() + '/' + dir
                #print('path: ' + path)
                if (not os.path.isdir(path)):
                    print('[setdir failed: ' + dir + ' does not exist.]')
                    continue
                
                print('[Successfully set ' + dir + ' as the directory for searching offered files.]')
                setup = True

            # offer functionality
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
                forServerSocket.sendto(message.encode(),(server_ip, server_port))

            # list functionality
            elif (command == "list"):
                if (len(client_table) == 0 or len(client_table[0]) == 0):
                    print('[No files available for download at the moment.]')
                else:
                    sorted_table = sorted(client_table, key=lambda x:x[0])
                    print("sorted table: " + str(sorted_table))
                    print("{:12s} {:10s} {:15s} {:10s}".format("FILENAME", "OWNER", "IP ADDRESS", "TCP PORT"))
                    for file in sorted_table:
                        print(("{:12s} {:10s} {:15s} {:10s}".format(file[0], file[1], file[2], file[3])))
            
            elif ("request" in command):
                items = command.split()
                if (len(items) != 3):
                    print('use: request <filename> <client>')
                    continue

                filename = items[1]
                client = items[2]
                
                # error checking
                if (client == name):
                    print('Error: Invalid Request')
                    continue

                flag = 1
                for file in client_table:
                    print(str(file))
                    if (file):
                        if (file[0] == filename and file[1] == client):
                            destination_IP = file[2]
                            destination_port = file[3]
                            flag = 0
                            break
                
                if (flag):
                    print('Error: Invalid Request')
                    continue

                # connect to client
                clientSocket = socket(AF_INET, SOCK_STREAM)
                clientSocket.connect((destination_IP, int(destination_port)))
                print('< Connection with ' + client + ' established. >')

                # request file
                message = filename + ' ' + name
                clientSocket.send(message.encode())

                # download file
                with open(filename, "wb") as f:
                    i = 0
                    while True:
                        bytes_read = clientSocket.recv(4096)
                        if not bytes_read:
                            break
                        f.write(bytes_read)
                        if (i == 0):
                            print('< Downloading ' + filename + '... >')
                        i = i + 1

                # finish download
                print('< ' + filename + ' downloaded successfully! >')

                # closed connection
                clientSocket.close()
                print('< Connection with ' + name + ' closed. >')

            else:
                print("Error: unsupported command")
                continue


    else:
        print('use: FileApp -s <port> or \
            use: FileApp -c <name> <server-ip> <server-port> <client-udp-port> <client-tcp-port>')
        sys.exit()
