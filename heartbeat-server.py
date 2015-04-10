#!/usr/bin/python
###########################################################
#WiFIDS - heartbeatserver.py							  #
#Heartbeat server to talk to WiFIDS						  #
#Roger Baker, Houston Hunt, Prashant Kumar, Garrett Miller#
#Some Crypto Functions inspired by:                       #
#https://launchkey.com/docs/api/encryption                #
###########################################################

import socket
import time #Needed for labeling date/time
import datetime #Needed for labeling date/time
import smtplib #Needed for sending alerts
from email.mime.text import MIMEText #Needed for sending alerts
from email.mime.image import MIMEImage #Needed for sending alerts
from email.mime.multipart import MIMEMultipart #Needed for sending alerts
from Crypto.PublicKey import RSA #Needed for crypto functions
from Crypto.Cipher import PKCS1_OAEP #Needed for crypto functions
from base64 import b64decode #Needed for crypto functions

#############################
#DEFINE PARAMETERS HERE		#
#############################
WIFIDS_IP = '127.0.0.1'
TCP_PORT = 18731
BUFFER_SIZE = 1024
MAGICMESSAGE = "I love WiFIDS!"
ALERTCONTACTS = ["rjbaker@andrew.cmu.edu",
"pkumar1@andrew.cmu.edu",
"hgh@andrew.cmu.edu",
"gmmiller@andrew.cmu.edu"]
#############################

#Encrypts message for security
def encrypt_RSA(public_key_loc, message):

	key = open(public_key_loc, "r").read()
	rsakey = RSA.importKey(key)
	rsakey = PKCS1_OAEP.new(rsakey)
	encrypted = rsakey.encrypt(message)
	return encrypted.encode('base64')

#Decrypts message for security	
def decrypt_RSA(private_key_loc, package):

	key = open(private_key_loc, "r").read() 
	rsakey = RSA.importKey(key) 
	rsakey = PKCS1_OAEP.new(rsakey) 
	decrypted = rsakey.decrypt(b64decode(package)) 
	return decrypted

#Sends Email for deauths (obviously)
def senddownmail(recipients, prettytime, cause):

	#Build the email
	message = MIMEMultipart()
	sender= "cmuwifids@gmail.com"
	text = MIMEText("""The heartbeat script has detected a problem with WiFIDS. The event was logged at:

	Time: """ + prettytime + """
	Cause: """ + cause + """
	
WiFIDS suggests investigating further.	
	
	""")
	message['Subject'] = "[WiFIDS] WiFIDS has a problem!"
	message['From'] = "WiFIDS <cmuwifids@gmail.com>"
	message['To'] = str(', '.join(recipients))
	message.attach(text)

	try:
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.starttls()
		server.login('cmuwifids','thepythonrappers!')
		server.sendmail(sender, recipients, str(message))
		print "Successfully sent downtime email to " + str(', '.join(recipients))
		server.quit()
	except:
		print "Error: unable to send downtime email to " + str(', '.join(recipients))

while True:
	#Get Time
	timestamp = int(time.time())
	prettytime = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
	
	#Set up the connection
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		server.connect((WIFIDS_IP, TCP_PORT))
	except:
		print "[" + prettytime + "] Can't connect. Sending Email."
		cause = "Unable to connect to WiFIDS via TCP."
		senddownmail(ALERTCONTACTS, prettytime, cause)
		break
	server.send(MAGICMESSAGE)
	receivedData = server.recv(BUFFER_SIZE)
	server.close()
	
	if receivedData == "I do too!":
		print "[" + prettytime + "] Everything is A-OK."
	else:
		print "[" + prettytime + "] Something isn't right. Sending Email."
		cause = "Incorrect response from WiFIDS."
		senddownmail(ALERTCONTACTS, prettytime, cause)
	time.sleep(30)
