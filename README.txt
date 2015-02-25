***********************************************************
*WiFiDS - A Wireless-Physical IDS with Jam Detection      *
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

Setup (on Debian-like OS):

sudo apt-get -y install python libssl-dev iw python-scapy tcpdump python-netaddr python-colorama python-picamera
cd /usr/share/pyshared/netaddr/eui && sudo python ./ieee.py

NOTE: You may have to add the main user to the "video" group to use the camera, if this isn't enabled by default.  To do this, run (as root, replacing 'username'): 

# usermod -G video <username>

=========================================================
RUNNING:
=========================================================

1) Set configuration parameters in settings.cfg.
2) Restart system with "sudo restart", or unplug and replug device.
3) In its configured state, "main.py" should execute on startup. If not, "sudo python main.py" will execute the main executable script.
