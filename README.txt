***********************************************************
*WiFIDS - A Wireless-Physical IDS with Jam Detection      *
*Roger Baker, Houston Hunt, Prashant Kumar, Garrett Miller*
*18-731, Spring 2015, Carnegie Mellon University          *
***********************************************************

=========================================================
INSTALLING:
=========================================================
Dependencies Required:

Python 2.X
libssl-dev
iw
tcpdump
libpcap 0.8+
python-netaddr
python-colorama
python-scapy
python-picamera
pi-motion-lite
python-sqlite
python-django
python-crypto

Setup (on Debian-like OS. Assumes presence of user 'wifids'):

cd /home/wifids/
tar -xvf wifids.tar
cd wifids/
mkdir images
chmod -R +xr *
sudo apt-get -y install python libssl-dev iw python-scapy tcpdump python-netaddr python-colorama python-picamera python-sqlite python-django python-crypto
cd /usr/share/pyshared/netaddr/eui && sudo python ./ieee.py

NOTE: You may have to add the user "wifids" to the "video" group to use the camera, if this isn't enabled by default.  To do this, run (as root): 
# usermod -G video wifids

=========================================================
RUNNING:
=========================================================
1) Set configuration parameters in settings.cfg.
2) Restart system with "sudo restart", or unplug and replug device.
3) Run "sudo python main.py" to execute the main executable script.

=========================================================
WEB INTERFACE:
=========================================================
1) Navigate to http://<WiFIDS IP>:6482

=========================================================
HEARTBEAT SCRIPT (with AES encryption):
=========================================================
1) Copy heartbeatserver.py to another host on your network.
2) Ensure pycrypto is installed - "sudo apt-get install python-crypto" (on Debian-like)
3) Make the script executable with "chmod +x heartbeatserver.py"
4) Modify the file, adding desired port and known IP of WiFIDS, as well as emails to notify. Change AES keys if desired.
5) Run "python heartbeatserver.py" - ensure WiFIDS is running first!

=========================================================
ACKNOWLEDGEMENTS:
=========================================================
pi-motion-lite is by Claude Pageau, https://github.com/pageauc
	Code has been modified for use within this project.
