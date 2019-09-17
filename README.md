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
- Model - your device model hex code, find your own in gendevice function (devtype == 0x????): https://github.com/mjg59/python-broadlink/blob/master/broadlink/__init__.py
- IPAddress - an IP address of RM 3 Mini (RM 3 Mini must have local IP address)
- Port - a port used for UDP communication (in most cases, 80)
- MACAddress - a MAC address of RM 3 Mini (should be in format: MM:MM:MM:SS:SS:SS)
- Timeout - a time in seconds script should wait for an answer after starting a learn process (should be less then 60 seconds)

[Commands]
- This section should be populated by using the script, not manually

Configuration file could optionally contain multiple device sections (with a custom names, must not contain any blanks). The device section must have all the parameters General section has. It allows user to control multiple RM 3 Minis without passing all the parameters separately (Model, IP Address, Port, MAC Address and Timeout). Instead, only -d (--device) parameter should be passed, with a section name containing connection parameters for the specific device. 

#### Example of a custom device section:
```
[RM3LivingRoom]
Model = 0x2737
IPAddress = 192.168.0.1
Port = 80
MACAddress = AA:BB:CC:DD:EE:FF
Timeout = 30
```

### Syntax and usage
```
BlackBeanControl.py -c <Command name> [-d <Device name>] [-o <Model>] [-i <IP Address>] [-p <Port>] [-m <MAC Address>] [-t <Timeout>] [-r <Re-key Command>]
```

Parameters explanation: 
- Command name - mandatory parameter. If the sript is called with a command name not contained in the configuration file (BlackBeanControl.ini), it will start a learning process. After putting RM 3 Mini in the learning state, IR command should be sent to RM 3 Mini (usually a button press on the remote control). When defined timout expires, captured IR command will be saved in the configuration file - in the [Commands] section. In case the script is called with a command name contained in the configuration file, it will send that command to RM 3 Mini.
- Device name - optional parameter. If the script is called with Device name parameter, Model, IP address, port, MAC address and timeout parameters found in the General section of the configuration file will be ignored, and a script will use parameters found in a device section of the configuration file. Device name parameter can not be used in conjunction with Model, IP Address, Port, MAC Address and Timeout command line parameters.
- Model - optional parameter. If the script is called with Model parameter, model found in the configuration file will be ignored, and a script will use model from this parameter.
- IP Address - optional parameter. If the script is called with IP Address parameter, IP address found in the configuration file will be ignored, and a script will use IP address from this parameter.
- Port - optional parameter. If the script is called with Port parameter, port found in the configuration file will be ignored, and a script will use port from this parameter.
- MAC Address - optional parameter. If the script is called with MAC address parameter, MAC address found in the configuration file will be ignored, and a script will use MAC address from this parameter.
- Timeout - optional parameter. If the script is called with Timeout parameter, Timeout found in the configuration file will be ignored, and a script will use Timeout from this parameter.
- Re-Key - optional parameter. This will re-key existing IR data to a new format that does not use the device key for storage. If the data was stored previously with a specific Broadlink device that device name will need to be provided for re-keying by providing a device name using -d parameter.

Model, IP Address, Port, MAC Address and Timeout command line parameters can not be used separately.

### Donations

This script is available for free under the GPL license. If you use the script, and would like to donate, feel free to send any amount through paypal. 

Note: Since standard Donate option is not available on my PayPal account this is a workaround solution.

[![Donate](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=CCZRY3C8RXSRW&lc=BA&item_name=Donation%20%2d%20BlackBeanControl&item_number=1&button_subtype=services&currency_code=EUR&bn=PP%2dBuyNowBF%3abtn_paynowCC_LG%2egif%3aNonHosted)

You can also donate some spare crypto to the following wallets:

BTC: 1FQ4XveJDkLCrFtaY5Fc7ir7nhH8mgiyKy

ETH: 0xfB8867a120EB916997B8249fe8e88Ea7BDAF5FA8

BCH: qzw7u3cxlujayc7aekpuem358qkpy084qgqlzrrar6

XRP: rMZVSmEVbfHxFcEHGZTvY1JHCTtHMnw1ga

XLM: GB3JHEKDJGGSVOBDSFJJ2KC4GNGHTDJULO7BYXEHMY3DGGQHLUGTQYBG

### License

Software licensed under GPL version 3 available on http://www.gnu.org/licenses/gpl.txt.
