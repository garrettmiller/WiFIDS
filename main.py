#!/usr/bin/python
###########################################################
#WiFIDS - main.py								          #
#Main Driver for WiFiDS                                   #
#Roger Baker, Houston Hunt, Prashant Kumar, Garrett Miller#
###########################################################

#Import all our functions
from functions import * 

#############################
#Set Port to run Webserver on
#############################
WEBPORT = 6482
#############################

#Check to see if we're root
if os.geteuid() != 0:
	exit("You need to have root privileges to run WiFIDS.\nPlease try again, but with 'sudo'. Exiting.")
	
#Delete old sqlite3 db.
rm = subprocess.call(['rm', 'wifids.db'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#Create new sqlite3 db and connect.
connection = sqlite3.connect('wifids.db')
cursor = connection.cursor()

#Build the database if necessary. Write changes to db and close, since the individual processes will access it later.
cursor.execute('CREATE TABLE IF NOT EXISTS probes (timestamp int, mac TEXT, rssi INT, ssid TEXT, oui TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS events (timestamp int, imagepath TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS deauths (timestamp int, mac TEXT, client TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS emaillog (timestamp int, mac TEXT)')
connection.commit()
connection.close()
	
#Clean up any leftover running airmon-ng and put wlan0 into monitor mode.
cleanup = subprocess.call(['iw', 'dev', 'mon0', 'del'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
startmon = subprocess.call(['iw', 'dev', 'wlan0', 'interface', 'add', 'mon0', 'type', 'monitor'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
monup = subprocess.call(['ifconfig', 'mon0', 'up'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#Start Web GUI
startweb = subprocess.Popen(['python', 'web/manage.py', 'runserver', '0.0.0.0:'+str(WEBPORT)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

#Start both functions simultaneously
p1 = Process(target=doMotionDetect)
p2 = Process(target=doPcap)
p3 = Process(target=runHeartbeat)
p1.start()
p2.start()
p3.start()
p1.join()
p2.join()
p3.join()
