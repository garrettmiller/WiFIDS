#!/usr/bin/python
###########################################################
#WiFiDS - heartbeatserver.py					          #
#Heartbeat server to talk to WiFIDS                       #
#Roger Baker, Houston Hunt, Prashant Kumar, Garrett Miller#
###########################################################

import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 18731
BUFFER_SIZE = 1024
MESSAGE = "I love WiFIDS!"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((TCP_IP, TCP_PORT))
server.send(MESSAGE)
receivedData = server.recv(BUFFER_SIZE)
server.close()

if receivedData == "I do too!":
	print "Everything is A-OK."
else:
	print "Something isn't right."
