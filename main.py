#!/usr/bin/python
###########################################################
#WiFiDS - main.py								          #
#Main Driver for WiFiDS                                   #
#Roger Baker, Houston Hunt, Prashant Kumar, Garrett Miller#
###########################################################

from functions import * #Our functions file

#Check to see if we're root
if os.geteuid() != 0:
	exit("You need to have root privileges to run WiFIDS.\nPlease try again, but with 'sudo'. Exiting.")
	
#Delete old sqlite3 db.
rm = subprocess.call(['rm', 'wifids.db'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#Create new sqlite3 db and connect.
connection = sqlite3.connect('wifids.db')
cursor = connection.cursor()

#Build the database if necessary. Write changes to db and close, since the individual processes will access it later.
cursor.execute('CREATE TABLE IF NOT EXISTS probes (timestamp TEXT, mac TEXT, rssi INT, ssid TEXT, oui TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS events (timestamp TEXT, imagepath TEXT)')
connection.commit()
connection.close()
	
#Clean up any leftover running airmon-ng and put wlan0 into monitor mode.
cleanup = subprocess.call(['iw', 'dev', 'mon0', 'del'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
startmon = subprocess.call(['iw', 'dev', 'wlan0', 'interface', 'add', 'mon0', 'type', 'monitor'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
monup = subprocess.call(['ifconfig', 'mon0', 'up'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#Start doing motion detection
def doMotionDetect():
	stream1 = getStreamImage()
	while True:
		stream2 = getStreamImage()
		#Do this when we see motion!
		if checkForMotion(stream1, stream2):
			print Fore.YELLOW + "Motion Detected!"
			
			#Initialize the camera class, take picture, close camera
			camera = picamera.PiCamera()
			camera.resolution = (1024, 768)
			camera.hflip = True
			camera.vflip = True
			timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			path="/var/www/images/"+timestamp+".jpg"
			camera.capture(path)
			camera.close()
			time.sleep(1)
			print Fore.BLUE + "Photo Taken!"
						
			#Add motion event information to database.
			connection = sqlite3.connect('wifids.db')
			cursor = connection.cursor()
			cursor.execute("INSERT INTO events VALUES (?,?)", (timestamp, path))
			connection.commit()
			connection.close()
								
			#Send Email
			sendList = []
			for key, alertContact in alertContacts:
				sendList.append(alertContact)
			sendmail(sendList, path)
		
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
