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
import datetime #Needed for labeling date/time

import time
import picamera.array
from fractions import Fraction

#Improves colorization compatibility, autoresets color after print.
init(autoreset=True)

#Declare empty list for observed clients 
observedClients = []

# Read Configuration File and define lists 
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
alertContacts = config.items("AlertContacts")
authorizedClients = config.items("AuthorizedClients")

##################################
#BEGIN MOTION DETECT FUNCTIONS   #
#Claude Pageau Dec-2014          #
##################################

#Constants
SECONDS2MICRO = 1000000  # Constant for converting Shutter Speed in Seconds to Microseconds

threshold = 10     # How Much a pixel has to change
sensitivity = 200  # How Many pixels need to change for motion detection
nightShut = 5.5    # seconds Night shutter Exposure Time default = 5.5  Do not exceed 6 since camera may lock up
nightISO = 800

testWidth = 100
testHeight = 75
if nightShut > 6:
	nightShut = 5.9
nightMaxShut = int(nightShut * SECONDS2MICRO)
nightMaxISO = int(nightISO)
nightSleepSec = 10  


def userMotionCode():
	print "Motion Found So Do Something ..."
	#Actually run the sniffer. store=0 is required to keep memory from filling with packets.
	sniff(iface='mon0', prn=runsniffer, store=0)
	return   
	
def showTime():
	rightNow = datetime.datetime.now()
	currentTime = "%04d%02d%02d-%02d:%02d:%02d" % (rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)
	return currentTime    
 
def checkForMotion(data1, data2):
	# Find motion between two data streams based on sensitivity and threshold
	motionDetected = False
	pixColor = 1 # red=0 green=1 blue=2
	pixChanges = 0;
	for w in range(0, testWidth):
		for h in range(0, testHeight):
			# get the diff of the pixel. Conversion to int
			# is required to avoid unsigned short overflow.
			pixDiff = abs(int(data1[h][w][pixColor]) - int(data2[h][w][pixColor]))
			if  pixDiff > threshold:
				pixChanges += 1
			if pixChanges > sensitivity:
				break; # break inner loop
		if pixChanges > sensitivity:
			break; #break outer loop.
	if pixChanges > sensitivity:
		motionDetected = True
	return motionDetected  
 
def getStreamImage(daymode):
	# Capture an image stream to memory based on daymode
	isDay = daymode
	with picamera.PiCamera() as camera:
		time.sleep(2)
		camera.resolution = (testWidth, testHeight)
		with picamera.array.PiRGBArray(camera) as stream:
			if isDay:
				camera.exposure_mode = 'auto'
				camera.awb_mode = 'auto' 
			else:
				# Take Low Light image            
				# Set a framerate of 1/6fps, then set shutter
				# speed to 6s and ISO to 800
				camera.framerate = Fraction(1, 6)
				camera.shutter_speed = nightMaxShut
				camera.exposure_mode = 'off'
				camera.iso = nightMaxISO
				# Give the camera a good long time to measure AWB
				# (you may wish to use fixed AWB instead)
				time.sleep( nightSleepSec )
			camera.capture(stream, format='rgb')
			return stream.array
			
##################################
#END MOTION DETECT FUNCTIONS     #
#Claude Pageau Dec-2014          #
##################################

						
########################
#BEGIN OUR FUNCTIONS   #
########################
def sendmail(recipients, mac, oui, timestamp):
	img_data = open('/var/www/images/'+timestamp+'.jpg', 'rb').read()
	message = MIMEMultipart()
	sender= "cmuwifids@gmail.com"
	text = MIMEText("""An unauthorized intrusion was detected into the secure area.  Intruder details:

	Location: Front Door
	Time: """ + timestamp + """
	MAC Address: """ + str(mac) + """
	Device Type: """ + oui + """

	A photo of the intrusion is attached.
	""")
	message['Subject'] = "[WiFIDS] Unauthorized Intrusion Detected!"
	message['From'] = "WiFIDS <cmuwifids@gmail.com>"
	message['To'] = str(', '.join(recipients))
	message.attach(text)
	image = MIMEImage(img_data, name=os.path.basename('images/'+timestamp+'.jpg'))
	message.attach(image)

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
					
					#Initialize the camera class, take picture, close camera
					camera = picamera.PiCamera()
					camera.resolution = (1024, 768)
					timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
					camera.capture('/var/www/images/'+timestamp+'.jpg')
					camera.close()
					
					#Send Email
					sendList = []
					for key, alertContact in alertContacts:
						sendList.append(alertContact)
					#sendmail(sendList, mac, oui, timestamp)