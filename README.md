# BlackBeanControl - Broadlink RM 3 Mini (aka Black Bean) control script

A simple Python 2 script, which uses python-broadlink package. It can be used for both, learning and sending IR commands

### Installation

Before cloning/downloading the script, you should install all dependencies: 

- Install configparser package: python -m pip install configparser
- Install netaddr package: python -m pip install netaddr
- Install pycrypto package: python -m pip install pycrypto
- Download python-broadlink package - you can find it on github by the package name (github user: mjg59)
- Unzip it to some local folder and install it: setup.py install

Now you can clone/download BlackBeanControl (in case you download it as archive, unzip it to some local folder).

### Configuration

All required configuration is held within BlackBeanControl.ini file. It consists of the following options: 

[General]
- IPAddress - an IP address of RM 3 Mini (RM 3 Mini must have local IP address)
- Port - a port used for UDP communication (in most cases, 80)
- MACAddress - a MAC address of RM 3 Mini (should be in format: MM:MM:MM:SS:SS:SS)
- Timeout - a time in seconds script should wait for an answer after starting a learn process (should be less then 60 seconds)

[Commands]
This section should be populated by using the script, not manually

### Syntax and usage

BlackBeanControl.py -c \<Command name> [-i \<IP Address>] [-p \<Port>] [-m \<MAC Address>]

Parameters explanation: 
- Command name - mandatory parameter. If the sript is called with a command name not contained in the configuration file (BlackBeanControl.ini), it will start a learning process. After putting RM 3 Mini in the learning state, IR command should be sent to RM 3 Mini (usually a button press on the remote control). When defined timout expires, captured IR command will be saved in the configuration file - in the [Commands] section. In case the script is called with a command name contained in the configuration file, it will send that command to RM 3 Mini.
- IP Address - optional parameter. If the script is called with IP Address parameter, IP address found in the configuration file will be ignored, and script will use IP address from this parameter
- Port - optional parameter. If the script is called with Port parameter, port found in the configuration file will be ignored, and script will use port from this parameter
- MAC Address - optional parameter. If the script is called with MAC address parameter, MAC address found in the configuration file will be ignored, and script will use MAC address from this parameter
