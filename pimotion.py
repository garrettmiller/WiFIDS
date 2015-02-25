##################################
#Adapted from Pi-motion-lite   	 #
#Claude Pageau Dec-2014			 #
#https://github.com/pageauc      #
##################################

import picamera.array #Needed to track motion
import time #Needed for keeping track of time
from fractions import Fraction #Needed to do fractions

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