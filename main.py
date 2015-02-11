#!/usr/bin/python

###########################################################
#WiFiDS - main.py								          #
#Main Driver for WiFiDS                                   #
#Roger Baker, Houston Hunt, Prashant Kumar, Garrett Miller#
###########################################################

import os #Needed to check UID for root.
import subprocess #Needed for system calls
from scapy.all import * #Needed to do 802.11 stuff
from netaddr import * #Needed for OUI lookup
import ConfigParser #Needed to parse config file
import string #Needed to work with strings
from colorama import Fore, init # Needed for terminal colorization

#Improves colorization compatibility, autoresets color after print.
init(autoreset=True)

#Check to see if we're root
if os.geteuid() != 0:
	exit("You need to have root privileges to run WiFIDS.\nPlease try again, but with 'sudo'. Exiting.")

#Clean up any leftover running airmon-ng and put wlan0 into monitor mode.
cleanup = subprocess.call(['airmon-ng', 'stop', 'mon0', 'mon1', 'mon2', 'mon3'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
startmon = subprocess.call(['airmon-ng', 'start', 'wlan0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Read Configuration File and define lists
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
alertContacts = config.items("AlertContacts")
authorizedClients = config.items("AuthorizedClients")

# Declare a Python list to keep track of client MAC addresses
observedClients = []

# The sniffmgmt() function is called each time Scapy receives a packet
def sniffmgmt(p):
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

			# Check our list and if client isn't there, add to list.
			# Also perform OUI lookup on MAC. Checks for invalid OUI.
			if p.addr2 not in observedClients:
				try:
					oui = EUI(p.addr2).oui.registration().org
				except:
					oui = "Invalid OUI"
				print p.addr2 +  " -- " + oui
				observedClients.append(p.addr2)

				#Iterate through config file items to see if device is authorized.
				for key, authorizedClient in authorizedClients:
					if str(mac) == string.lower(authorizedClient):
						authorizedFlag = 1
						break
					else:
						authorizedFlag = 0
					
				#Perform appropriate action.
				if authorizedFlag == 1:
					print Fore.GREEN + "Authorized Device - " + str(mac)
				else:
					print Fore.RED + "!!!WARNING - Device " + str(mac) + " is unauthorized!!!"
				
#Actually run the sniffer. store=0 is required to keep memory from filling with packets.
sniff(iface='mon0', prn=sniffmgmt, store=0)
