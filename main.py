###########################################################
#WiFiDS - main.py								          #
#Main Driver for WiFiDS                                   #
#Roger Baker, Houston Hunt, Prashant Kumar, Garrett Miller#
###########################################################
#!/usr/bin/python

import os #Needed to check UID for root.
import subprocess #Needed for system calls
from scapy.all import * #Needed to do 802.11 stuff
from time import sleep

#Check to see if we're root
if os.geteuid() != 0:
	exit("You need to have root privileges to run WiFIDS.\nPlease try again, but with 'sudo'. Exiting.")

#Clean up any leftover running airmon-ng, airodump
proc = subprocess.call(['killall', 'airodump-ng'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
proc = subprocess.call(['airmon-ng', 'stop', 'mon0', 'mon1', 'mon2', 'mon3'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#Put wlan0 into monitor mode.
proc = subprocess.call(['airmon-ng', 'start', 'wlan0'], stdout=subprocess.PIPE)

# Next, declare a Python list to keep track of client MAC addresses
# that we have already seen so we only print the address once per client.
observedclients = []

# The sniffmgmt() function is called each time Scapy receives a packet
# (we'll tell Scapy to use this function below with the sniff() function).
# The packet that was sniffed is passed as the function argument, "p".
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

			# We only want to print the MAC address of the client if it
			# hasn't already been observed. Check our list and if the
			# client address isn't present, print the address and then add
			# it to our list.
			if p.addr2 not in observedclients:
				print("p.addr2")
				observedclients.append(p.addr2)

# With the sniffmgmt() function complete, we can invoke the Scapy sniff()
# function, pointing to the monitor mode interface, and telling Scapy to call
# the sniffmgmt() function for each packet received. Easy!
sniff(iface=interface, prn=sniffmgmt)

