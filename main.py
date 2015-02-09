#!/usr/bin/python

###########################################################
#WiFiDS - main.py								          #
#Main Driver for WiFiDS                                   #
#Roger Baker, Houston Hunt, Prashant Kumar, Garrett Miller#
###########################################################

import os #Needed to check UID for root.
import subprocess #Needed for system calls
from scapy.all import * #Needed to do 802.11 stuff
from time import sleep

#Check to see if we're root
if os.geteuid() != 0:
	exit("You need to have root privileges to run WiFIDS.\nPlease try again, but with 'sudo'. Exiting.")

#Clean up any leftover running airmon-ng, airodump
proc = subprocess.call(['airmon-ng', 'stop', 'mon0', 'mon1', 'mon2', 'mon3'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#Put wlan0 into monitor mode.
proc = subprocess.call(['airmon-ng', 'start', 'wlan0'], stdout=subprocess.PIPE)

# Declare a Python list to keep track of client MAC addresses
observedclients = []

# THIS SECTION FOR LEARNING PURPOSES ONLY
# SOME EXAMPLE CODE BORROWED FROM http://pen-testing.sans.org/blog/2011/10/13/special-request-wireless-client-sniffing-with-scapy

# The sniffmgmt() function is called each time Scapy receives a packet
def sniffmgmt(p):

	# Define our tuple (an immutable list) of the 3 management frame
	# subtypes sent exclusively by clients. I got this list from Wireshark.
	stamgmtstypes = (0, 2, 4)

	# Make sure the packet has the Scapy Dot11 layer present
	if p.haslayer(Dot11):

		# Check to make sure this is a management frame (type=0) and that
		# the subtype is one of our management frame subtypes indicating a
		# a wireless client
		if p.type == 0 and p.subtype in stamgmtstypes:

			# Check our list and if client isn't there, add to list.
			if p.addr2 not in observedclients:
				print(p.addr2)
				observedclients.append(p.addr2)

sniff(iface='mon0', prn=sniffmgmt)

