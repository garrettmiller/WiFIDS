#!/usr/bin/python

###########################################################
#WiFiDS - main.py								          #
#Main Driver for WiFiDS                                   #
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
import picamera #Needed to use camera functionality
import datetime #Needed for labeling date/time

#Improves colorization compatibility, autoresets color after print.
init(autoreset=True)

#Check to see if we're root
if os.geteuid() != 0:
	exit("You need to have root privileges to run WiFIDS.\nPlease try again, but with 'sudo'. Exiting.")

#Clean up any leftover running airmon-ng and put wlan0 into monitor mode.
cleanup = subprocess.call(['iw', 'dev', 'mon0', 'del'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
startmon = subprocess.call(['iw', 'dev', 'wlan0', 'interface', 'add', 'mon0', 'type', 'monitor'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
monup = subprocess.call(['ifconfig', 'mon0', 'up'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Read Configuration File and define lists 
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
alertContacts = config.items("AlertContacts")
authorizedClients = config.items("AuthorizedClients")

#Declare empty list for observed clients 
observedClients = []

def sendmail(recipients, mac, oui):
	sender= "cmuwifids@gmail.com"
	message = MIMEText("""An unauthorized intrusion was detected into the secure area.  Intruder details:

	Location: Front Door
	MAC Address: """ + str(mac) + """
	Device Type: """ + oui + """

	A photo of the intrusion is attached.
	""")
	message['Subject'] = "[WiFIDS] Unauthorized Intrusion Detected!"
	message['From'] = "WiFIDS <cmuwifids@gmail.com>"
	message['To'] = str(', '.join(recipients))
	
	try:
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.starttls()
		server.login('cmuwifids','thepythonrappers!')
		server.sendmail(sender, recipients, str(message))
		print "Successfully sent email to " + str(', '.join(recipients))
		server.quit()
	except:
		print "Error: unable to send email to " + str(', '.join(recipients))

# runsniffer() function is called each time Scapy receives a packet
def runsniffer(p):
	#Reinitialize "authorizedFlag"
	authorizedFlag = 0

	# Define our tuple of the 3 management frame
	# subtypes sent exclusively by clients. From Wireshark.
	managementFrameTypes = (0, 2, 4)

	# Make sure the packet is a WiFi packet
	if p.haslayer(Dot11):

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
				print mac +  " -- " + oui
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
					print Fore.GREEN + "Authorized Device - " + str(mac) + " RSSI: " + str(rssi)
				else: #Someone is unauthorized!
					print Fore.RED + "!!!WARNING - Device " + str(mac) + " is unauthorized!!!" + " RSSI: " + str(rssi)
					
					#Initialize the camera class, take picture
					camera = picamera.PiCamera()
					camera.resolution = (1024, 768)
					timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
					camera.capture('images/'+timestamp+'.jpg')
					camera.close()
					
					#Send Email
					sendList = []
					for key, alertContact in alertContacts:
						sendList.append(alertContact)
					#sendmail(sendList, mac, oui)

#Actually run the sniffer. store=0 is required to keep memory from filling with packets.
sniff(iface='mon0', prn=runsniffer, store=0)
