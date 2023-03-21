#!/usr/bin/env python3.10

from socket import *
import sys

# Get command line arguments
try:
    listen_port = int(sys.argv[1])
    fake_ip = sys.argv[2]
    server_ip = sys.argv[3]
except:
    print('use: ./proxy <listen-port> <fake-ip> <server-ip>')
    sys.exit()

listenSocket = socket(AF_INET,SOCK_STREAM) ## LISTENING SOCKET
listenSocket.bind(('',listen_port)) # listens on any IP address on specified port
listenSocket.listen(10) # Accepts 10 sequential connections

while True:
        # Establish connection with client
        clientSideSocket, addr = listenSocket.accept() ## RETURNS CONNECTION SOCKET

        # Establish connection with server
        serverSideSocket = socket(AF_INET, SOCK_STREAM)
        serverSideSocket.bind((fake_ip, 0))
        serverSideSocket.connect((server_ip,8080))

        while True:

                # get message from client
                try:
                        message = clientSideSocket.recv(2048)
                except:
                        clientSideSocket.close()
                        serverSideSocket.close()
                        break

                # forward message to server
                try:
                        serverSideSocket.send(message)
                        returnedMessage = serverSideSocket.recv(2048)
                except:
                        clientSideSocket.close()
                        serverSideSocket.close()
                        break

                # forward message to client
                try:
                        clientSideSocket.send(returnedMessage)
                except:
                        clientSideSocket.close()
                        serverSideSocket.close()
                        break