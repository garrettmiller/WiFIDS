#!/usr/bin/python
###########################################################
#WiFiDS - pimotion.py									  #
#Adapted from Pi-motion-lite, for WiFIDS                  #
#originally by Claude Pageau Dec-2014					  #
#https://github.com/pageauc                     		  #
#Modified By:											  #
#Roger Baker, Houston Hunt, Prashant Kumar, Garrett Miller#
###########################################################

import picamera.array #Needed to track motion
import time #Needed for keeping track of time

threshold = 10     # How Much a pixel has to change
sensitivity = 200  # How Many pixels need to change for motion detection
testWidth = 100
testHeight = 75

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
 
def getStreamImage():
	# Capture an image stream to memory based on daymode
	with picamera.PiCamera() as camera:
		time.sleep(2)
		camera.resolution = (testWidth, testHeight)
		with picamera.array.PiRGBArray(camera) as stream:
			camera.exposure_mode = 'auto'
			camera.awb_mode = 'auto' 
			camera.capture(stream, format='rgb')
			camera.close()
			return stream.array
