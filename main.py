#!/usr/bin/python
###########################################################
#WiFiDS - main.py								          #
#Main Driver for WiFiDS                                   #
#Roger Baker, Houston Hunt, Prashant Kumar, Garrett Miller#
###########################################################

#TODO: Implement Multiprocess - Garrett

from functions import *

#Check to see if we're root
if os.geteuid() != 0:
	exit("You need to have root privileges to run WiFIDS.\nPlease try again, but with 'sudo'. Exiting.")
	
#Clean up any leftover running airmon-ng and put wlan0 into monitor mode.
cleanup = subprocess.call(['iw', 'dev', 'mon0', 'del'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
startmon = subprocess.call(['iw', 'dev', 'wlan0', 'interface', 'add', 'mon0', 'type', 'monitor'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
monup = subprocess.call(['ifconfig', 'mon0', 'up'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#Start doing motion detection
stream1 = getStreamImage()
while True:
	stream2 = getStreamImage()
	if checkForMotion(stream1, stream2):
		motionCode()
	stream2 = stream1
