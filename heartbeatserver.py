#!/usr/bin/python
###########################################################
#WiFIDS - heartbeatserver.py					          #
#Heartbeat server to talk to WiFIDS                       #
#Roger Baker, Houston Hunt, Prashant Kumar, Garrett Miller#
###########################################################

import socket
import time #Needed for labeling date/time
import datetime #Needed for labeling date/time
import smtplib #Needed for sending alerts
from email.mime.text import MIMEText #Needed for sending alerts
from email.mime.image import MIMEImage #Needed for sending alerts
from email.mime.multipart import MIMEMultipart #Needed for sending alerts

#############################
#DEFINE PARAMETERS HERE     #
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

#Sends Email for deauths (obviously)
def senddownmail(recipients, prettytime):

	#Build the email
	message = MIMEMultipart()
	sender= "cmuwifids@gmail.com"
	text = MIMEText("""The heartbeat script has detected that WiFIDS is unresponsive. The event was logged at:

	Time: """ + prettytime + """
	
WiFIDS suggests investigating further.	
	
	""")
	message['Subject'] = "[WiFIDS] WiFIDS is Down!"
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
		senddownmail(ALERTCONTACTS, prettytime)
		break
	server.send(MAGICMESSAGE)
	receivedData = server.recv(BUFFER_SIZE)
	server.close()
	
	if receivedData == "I do too!":
		print "[" + prettytime + "] Everything is A-OK."
	else:
		print "[" + prettytime + "] Something isn't right. Sending Email."
		senddownmail(ALERTCONTACTS, prettytime)
	time.sleep(30)
