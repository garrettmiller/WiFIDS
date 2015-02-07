###########################################################
#WiFiDS - main.py								          #
#Main Driver for WiFiDS                                   #
#Roger Baker, Houston Hunt, Prashant Kumar, Garrett Miller#
###########################################################
#!/usr/bin/python

import os	#Needed for cleanup system call
import subprocess #Needed for system calls

#Clean up any leftover running airmon-ng, airodump
proc = subprocess.Popen(['killall', 'airodump-ng'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
proc=subprocess.Popen(['airmon-ng', 'stop', 'mon0', 'mon1', 'mon2', 'mon3'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#Put wlan0 into monitor mode.
proc=subprocess.Popen(['airmon-ng', 'start', 'wlan0'], stdout=subprocess.PIPE)

#Start an Airodump capture
proc = subprocess.Popen(['airodump-ng', 'mon0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


