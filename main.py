#!/usr/bin/python
###########################################################
#WiFiDS - main.py								          #
#Main Driver for WiFiDS                                   #
#Roger Baker, Houston Hunt, Prashant Kumar, Garrett Miller#
###########################################################

#TODO: Implement Multiprocess - Garrett
from multiprocessing import Process
from functions import *

#Check to see if we're root
if os.geteuid() != 0:
	exit("You need to have root privileges to run WiFIDS.\nPlease try again, but with 'sudo'. Exiting.")
	
#Clean up any leftover running airmon-ng and put wlan0 into monitor mode.
cleanup = subprocess.call(['iw', 'dev', 'mon0', 'del'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
startmon = subprocess.call(['iw', 'dev', 'wlan0', 'interface', 'add', 'mon0', 'type', 'monitor'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
monup = subprocess.call(['ifconfig', 'mon0', 'up'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#Start doing motion detection
def doMotionDetect():
	stream1 = getStreamImage()
	while True:
		stream2 = getStreamImage()
		if checkForMotion(stream1, stream2):
			print Fore.YELLOW + "Motion Detected!"
			#Initialize the camera class, take picture, close camera
			camera = picamera.PiCamera()
			camera.resolution = (1024, 768)
			timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			camera.capture('/var/www/images/'+timestamp+'.jpg')
			camera.close()
			time.sleep(1)
			print Fore.BLUE + "Photo Taken!"
		stream2 = stream1
		
def doPcap():
	#Actually run the sniffer. store=0 is required to keep memory from filling with packets.
	sniff(iface='mon0', prn=runsniffer, store=0)

#Start both functions simultaneously
p1 = Process(target=doMotionDetect)
p2 = Process(target=doPcap)
p1.start()
p2.start()
p1.join()
p2.join()


