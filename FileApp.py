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