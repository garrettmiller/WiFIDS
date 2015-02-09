***********************************************************
*WiFiDS - A Wireless-Physical IDS with Jam Detection      *
*Roger Baker, Houston Hunt, Prashant Kumar, Garrett Miller*
*18-731, Spring 2015, Carnegie Mellon University          *
***********************************************************

=========================================================
INSTALLING:
=========================================================
Dependencies Required:

apt-get -y install python, libssl-dev, iw, aircrack-ng, python-scapy, tcpdump

If Aircrack-ng not in repositories, build from source with make && make install.

=========================================================
RUNNING:
=========================================================

1) Set configuration parameters in settings.cfg.
2) Restart system with "sudo restart", or unplug and replug device.
3) In its configured state, "main.py" should execute on startup. If not, "sudo python main.py" will execute the main executable script.
