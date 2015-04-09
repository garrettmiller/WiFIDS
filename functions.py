#!/usr/bin/python
###########################################################
#WiFiDS - functions.py							          #
#Functions library for WiFiDS                             #
#Roger Baker, Houston Hunt, Prashant Kumar, Garrett Miller#
###########################################################

import os #Needed to check UID for root.
import subprocess #Needed for system calls
import logging #Needed for logging tasks
logging.getLogger("scapy.runtime").setLevel(logging.ERROR) #Suppress initial Scapy IPv6 warning
from scapy.all import * #Needed to do 802.11 stuff
from netaddr import * #Needed for OUI lookup
import ConfigParser #Needed to parse config file
import string #Needed to work with strings
from colorama import Fore, init # Needed for terminal colorization
import smtplib #Needed for sending alerts
from email.mime.text import MIMEText #Needed for sending alerts
from email.mime.image import MIMEImage #Needed for sending alerts
from email.mime.multipart import MIMEMultipart #Needed for sending alerts
import picamera #Needed to use camera functionality
import time #Needed for timing on/off of things
import datetime #Needed for labeling date/time
import sqlite3 #Needed for local database
import RPi.GPIO as gpio #Needed to access Raspberry Pi GPIO Pins
from multiprocessing import Process #Needed for function concurrency
from pimotion import * #Needed for motion detection

#Cleanup any running gpio
gpio.cleanup

#Improves colorization compatibility, autoresets color after print.
init(autoreset=True)

#Declare empty list for observed clients 
observedClients = []

#Read Configuration File and define lists 
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
alertContacts = config.items("AlertContacts")
authorizedClients = config.items("AuthorizedClients")
protectedAPS = config.items("ProtectedAPS")

#Start doing motion detection
def doMotionDetect():
	cycle = 0
	stream1 = getStreamImage()
	while True:
		stream2 = getStreamImage()
		#Do this when we see motion!
		if checkForMotion(stream1, stream2):
			print Fore.YELLOW + "Motion Detected - ",
			
			#Initialize the camera class, take picture, close camera
			camera = picamera.PiCamera()
			camera.resolution = (1024, 768)
			camera.hflip = True
			camera.vflip = True
			timestamp = int(time.time())
			prettytime = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
			path="images/"+prettytime+".jpg"
			camera.capture(path)
			camera.close()
			time.sleep(1)
			print Fore.YELLOW + "Photo Taken!"
						
			#Add motion event information to database.
			connection = sqlite3.connect('wifids.db')
			cursor = connection.cursor()
			cursor.execute("INSERT INTO events VALUES (?,?)", (timestamp, path))
			connection.commit()
			connection.close()
								
			#Send Email
			sendList = []
			for key, alertContact in alertContacts:
				sendList.append(alertContact)
			#sendmail(sendList, path)

			#Initiate a counter to keep motion detection image fresh.
			cycle = cycle + 1
			if cycle >= 3:
				print ("3 modetect cycles completed. Refreshing modetect image")
				cycle = 0
				stream1 = getStreamImage()
			stream2 = stream1

		stream2 = stream1

#Make Noise
def soundBuzzer():
	gpio.setwarnings(False)
	gpio.setmode(gpio.BOARD)
	gpio.setup(11,gpio.OUT)
	for i in range(0,5):
		gpio.output(11,0)
		time.sleep(.05)
		gpio.output(11,1)
		time.sleep(.05)
		gpio.output(11,0)
	time.sleep(.5)
	gpio.cleanup
		
def doPcap():
	#Actually run the sniffer. store=0 is required to keep memory from filling with packets.
	sniff(iface='mon0', prn=runsniffer, store=0)
	
#Sends Email for deauths (obviously)
def senddeauthmail(recipients, timestamp, mac, client):

	#Build the email
	message = MIMEMultipart()
	sender= "cmuwifids@gmail.com"
	text = MIMEText("""A mass-deauthentication attack was detected against a protected AP. Details are as follows:

	Time: """ + datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') + """
	Affected AP: """ + str(mac) + """
	Observed Client (Likely Spoofed): """ + client + """
	
	WiFIDS suggests investigating further.	
	
	""")
	message['Subject'] = "[WiFIDS] Deauth Attack Detected!"
	message['From'] = "WiFIDS <cmuwifids@gmail.com>"
	message['To'] = str(', '.join(recipients))
	message.attach(text)

	try:
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.starttls()
		server.login('cmuwifids','thepythonrappers!')
		server.sendmail(sender, recipients, str(message))
		print "Successfully sent deauth email to " + str(', '.join(recipients))
		server.quit()
	except:
		print "Error: unable to send deauth email to " + str(', '.join(recipients))

#Sends Email for intruders (obviously)
def sendintrudermail(recipients, path):
	
	#Get last intrusion event from DB
	connection = sqlite3.connect('wifids.db')
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM probes ORDER BY timestamp DESC LIMIT 1;")
	result = cursor.fetchone()
	connection.close()

	#Build the email
	img_data = open(path).read()
	message = MIMEMultipart()
	sender= "cmuwifids@gmail.com"
	text = MIMEText("""An unauthorized intrusion was detected into the secure area.  Intruder details:

	Location: Front Door
	Time: """ + datetime.datetime.fromtimestamp(result[0]).strftime('%Y-%m-%d %H:%M:%S') + """
	MAC Address: """ + str(result[1]) + """
	Device Type: """ + result[4] + """

	A photo of the intrusion is attached.
	""")
	message['Subject'] = "[WiFIDS] Unauthorized Intrusion Detected!"
	message['From'] = "WiFIDS <cmuwifids@gmail.com>"
	message['To'] = str(', '.join(recipients))
	message.attach(text)
	image = MIMEImage(img_data, name=str(result[0]+'.jpg'))
	message.attach(image)

	try:
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.starttls()
		server.login('cmuwifids','thepythonrappers!')
		server.sendmail(sender, recipients, str(message))
		print "Successfully sent intruder email to " + str(', '.join(recipients))
		server.quit()
	except:
		print "Error: unable to send intruder email to " + str(', '.join(recipients))

# runsniffer() function is called each time Scapy receives a packet
def runsniffer(p):
	#Reinitialize "authorizedFlag", "protectedFlag"
	authorizedFlag = 0
	protectedFlag = 0
	maxTime = 0
	minTime = 0
	freshflag = 0

	# Define our tuple of the 3 management frame
	# subtypes sent exclusively by clients. From Wireshark.
	managementFrameTypes = (0, 2, 4)

	# Make sure the packet is a WiFi packet
	if p.haslayer(Dot11):
	
		#Do deauth detection
		if p.haslayer(Dot11Deauth):
			# Look for a deauth packet and print the AP BSSID, Client BSSID and the reason for the deauth.
			print Fore.CYAN + p.sprintf("Deauth found for AP [%Dot11.addr2%], Client [%Dot11.addr1%], Reason [%Dot11Deauth.reason%]")
			
			#Set MAC to what we received
			mac = p.addr2
			client = p.addr1
			
			#Iterate through config file items to see if device is authorized.
			for key, protectedAP in protectedAPS:
				if str(mac) == string.lower(protectedAP):
					protectedFlag = 1
					break
				else:
					protectedFlag = 0
			
			if protectedFlag == 1:
				#Be careful! We may be being deauthed, or this may be legitimate. Watch for more.
				timestamp = int(time.time())
				
				#Add deauth event information to database.
				connection = sqlite3.connect('wifids.db')
				cursor = connection.cursor()
				cursor.execute("INSERT INTO deauths VALUES (?, ?, ?)", (timestamp, mac, client))
				connection.commit()

				#Get numrows
				cursor.execute("SELECT COUNT(*) FROM deauths WHERE mac LIKE (?) LIMIT 10", (mac,))
				result=cursor.fetchone()
				numrows=result[0]
				
				#Check to see if this hits threshold to be defined as an "attack"
				cursor.execute("SELECT * FROM deauths WHERE mac LIKE (?) LIMIT 10", (mac,))
				result = cursor.fetchall()
				
				#Make sure we have 10 packets, then find time difference between highest/lowest.
				if numrows >= 10:
					for row in result:
						if row[0] > maxTime:
							maxTime = row[0]
					
					#Need to make sure this is no longer zero for comparison purposes		
					minTime = maxTime
					
					for row in result:
						if row[0] < minTime:
							minTime = row[0]
							
					#If enough packets happen in enough time, it's an attack.
					if (maxTime - minTime) < 10:
						print Fore.RED + "DEAUTH ATTACK DETECTED.",

						#Have we already emailed about this event? If not, don't do it again.
						cursor.execute("SELECT * FROM emaillog WHERE mac LIKE (?) LIMIT 1", (mac,))
						result = cursor.fetchone()
						if result == None:
							print "New Event. Sending Email..."
							freshflag = 1
						else:
							if (timestamp - result[0]) > 600:
								print "Old ongoing attack. Sending another Email..."
								freshflag = 1
						
						if freshflag == 1:
							#Get ready to send email, and add email log to database.
							sendList = []
							for key, alertContact in alertContacts:
								sendList.append(alertContact)
							senddeauthmail(sendList, timestamp, mac, client)
							cursor.execute("INSERT INTO emaillog VALUES (?, ?)", (timestamp, mac))
							connection.commit()
						else:
							print Fore.RED + "ALREADY REPORTED. ATTACK ONGOING."

				connection.close()

		# Check to make sure this is a management frame (type=0) and that
		# the subtype is one of our management frame subtypes
		if p.type == 0 and p.subtype in managementFrameTypes:

			#Set MAC to what we received
			mac = p.addr2

			#Define RSSI, we have to manually carve this out.
			rssi = (ord(p.notdecoded[-4:-3])-256)

			# Check our list and if client isn't there, add to list.
			# Also perform OUI lookup on MAC. Checks for invalid OUI.
			if p.addr2 not in observedClients:
				try:
					oui = EUI(mac).oui.registration().org
				except:
					oui = "Invalid/Unknown OUI"
				print "["+ mac + "] " + oui + " -",
				observedClients.append(mac)

				#Iterate through config file items to see if device is authorized.
				for key, authorizedClient in authorizedClients:
					if str(mac) == string.lower(authorizedClient):
						authorizedFlag = 1
						break
					else:
						authorizedFlag = 0

				#Perform appropriate action.
				if authorizedFlag == 1:
					print Fore.GREEN + "Authorized Device - RSSI: " + str(rssi)
				else: #Someone is unauthorized!
					print Fore.RED + "WARNING - Device is unauthorized! - RSSI: " + str(rssi)
					timestamp = int(time.time())
					prettytime = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
					soundBuzzer()
					
					#Add unauthorized event information to database.
					connection = sqlite3.connect('wifids.db')
					cursor = connection.cursor()
					connection.text_factory = str
					cursor.execute("INSERT INTO probes VALUES (?, ?, ?, ?, ?)", (timestamp, mac, str(rssi), str(p.info), oui))
					connection.commit()
					connection.close()
