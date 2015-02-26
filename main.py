#!/usr/bin/python
###########################################################
#WiFiDS - main.py								          #
#Main Driver for WiFiDS                                   #
#Roger Baker, Houston Hunt, Prashant Kumar, Garrett Miller#
###########################################################

from functions import *

#Check to see if we're root
if os.geteuid() != 0:
	exit("You need to have root privileges to run WiFIDS.\nPlease try again, but with 'sudo'. Exiting.")
	
#Clean up any leftover running airmon-ng and put wlan0 into monitor mode.
cleanup = subprocess.call(['iw', 'dev', 'mon0', 'del'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
startmon = subprocess.call(['iw', 'dev', 'wlan0', 'interface', 'add', 'mon0', 'type', 'monitor'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
monup = subprocess.call(['ifconfig', 'mon0', 'up'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#What to do when we actually see motion
def motionCode():
	#Actually run the sniffer. store=0 is required to keep memory from filling with packets.
	sniff(iface='mon0', prn=runsniffer, store=0)
	return 

#Start motion detection:
dayTime = True
stream1 = getStreamImage(dayTime)
while True:
	stream2 = getStreamImage(dayTime)
	if checkForMotion(stream1, stream2):
		motionCode()
	stream2 = stream1
