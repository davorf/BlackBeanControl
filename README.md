# BlackBeanControl - Broadlink RM 3 Mini (aka Black Bean) control script

A simple Python 2 script, which uses python-broadlink package. It can be used for both, learning and sending IR commands

### Installation

Before cloning/downloading the script, you should install all dependencies: 

Prerequisites for Linux users:

- Install pip package: 
      * wget https://bootstrap.pypa.io/get-pip.py 
      * Run get-pip.py
- Install python-dev package: apt-get install python-dev

Prerequisites for Windows users:

- Install Microsoft Visual C++ Compiler for Python 2.7
      * Download https://www.microsoft.com/en-us/download/details.aspx?id=44266
      * Run VCforPython27.msi

Dependencies for Windows/Linux:

- Install configparser package: python -m pip install configparser
- Install netaddr package: python -m pip install netaddr
- Install pycrypto package: python -m pip install pycrypto
- Download python-broadlink package - you can find it on the github by the package name (github user: mjg59)
- Unzip it to some local folder and install it: setup.py install

Now you can clone/download BlackBeanControl (in case you download it as archive, unzip it to some local folder).

### Configuration

All required configuration is held within BlackBeanControl.ini file. It consists of the following parameters: 

[General]
- IPAddress - an IP address of RM 3 Mini (RM 3 Mini must have local IP address)
- Port - a port used for UDP communication (in most cases, 80)
- MACAddress - a MAC address of RM 3 Mini (should be in format: MM:MM:MM:SS:SS:SS)
- Timeout - a time in seconds script should wait for an answer after starting a learn process (should be less then 60 seconds)

[Commands]
- This section should be populated by using the script, not manually

Configuration file could optionally contain multiple device sections (with a custom names, must not contain any blanks). The device section must have all the parameters General section has. It allows user to control multiple RM 3 Minis without passing all the parameters separately (IP Address, Port, MAC Address and Timeout). Instead, only -d (--device) parameter should be passed, with a section name containing connection parameters for the specific device. 

#### Example of a custom device section:
```
[RM3LivingRoom]
IPAddress = 192.168.0.1
Port = 80
MACAddress = AA:BB:CC:DD:EE:FF
Timeout = 30
```

### Syntax and usage
```
BlackBeanControl.py -c <Command name> [-d <Device name>] [-i <IP Address>] [-p <Port>] [-m <MAC Address>] [-t <Timeout>] [-r <Re-key Command>]
```

Parameters explanation: 
- Command name - mandatory parameter. If the sript is called with a command name not contained in the configuration file (BlackBeanControl.ini), it will start a learning process. After putting RM 3 Mini in the learning state, IR command should be sent to RM 3 Mini (usually a button press on the remote control). When defined timout expires, captured IR command will be saved in the configuration file - in the [Commands] section. In case the script is called with a command name contained in the configuration file, it will send that command to RM 3 Mini.
- Device name - optional parameter. If the script is called with Device name parameter, IP address, port, MAC address and timeout parameters found in the General section of the configuration file will be ignored, and a script will use parameters found in a device section of the configuration file. Device name parameter can not be used in conjunction with IP Address, Port, MAC Address and Timeout command line parameters.
- IP Address - optional parameter. If the script is called with IP Address parameter, IP address found in the configuration file will be ignored, and a script will use IP address from this parameter.
- Port - optional parameter. If the script is called with Port parameter, port found in the configuration file will be ignored, and a script will use port from this parameter.
- MAC Address - optional parameter. If the script is called with MAC address parameter, MAC address found in the configuration file will be ignored, and a script will use MAC address from this parameter.
- Timeout - optional parameter. If the script is called with Timeout parameter, Timeout found in the configuration file will be ignored, and a script will use Timeout from this parameter.
- Re-Key - optional parameter. This will re-key existing IR data to a new format that does not use the device key for storage. If the data was stored previously with a specific Broadlink device that device name will need to be provided for re-keying by providing a device name using -d parameter.

IP Address, Port, MAC Address and Timeout command line parameters can not be used separately.
