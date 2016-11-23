#!python2

import broadlink, configparser
import sys, getopt
import time, binascii
import netaddr
import Settings
from os import path
from Crypto.Cipher import AES

SettingsFile = configparser.ConfigParser()
SettingsFile.optionxform = str
SettingsFile.read(Settings.BlackBeanControlSettings)

SentCommand = ''
DeviceName=''
DeviceIPAddress = ''
DevicePort = ''
DeviceMACAddres = ''
DeviceTimeout = ''
AlternativeIPAddress = ''
AlternativePort = ''
AlternativeMACAddress = ''
AlternativeTimeout = ''

try:
    Options, args = getopt.getopt(sys.argv[1:], 'c:d:i:p:m:t:h', ['command=','device=','ipaddress=','port=','macaddress=','timeout=','help'])
except getopt.GetoptError:
    print('BlackBeanControl.py -c <Command name> [-d <Device name>] [-i <IP Address>] [-p <Port>] [-m <MAC Address>] [-t <Timeout>]')
    sys.exit(2)

for Option, Argument in Options:
    if Option in ('-h', '--help'):
        print('BlackBeanControl.py -c <Command name> [-d <Device name>] [-i <IP Address>] [-p <Port>] [-m <MAC Address>] [-t <Timeout>')
        sys.exit()
    elif Option in ('-c', '--command'):
        SentCommand = Argument
    elif Option in ('-d', '--device'):
        DeviceName = Argument
    elif Option in ('-i', '--ipaddress'):
        AlternativeIPAddress = Argument
    elif Option in ('-p', '--port'):
        AlternativePort = Argument
    elif Option in ('-m', '--macaddress'):
        AlternativeMACAddress = Argument
    elif Option in ('-t', '--timeout'):
        AlternativeTimeout = Argument

if SentCommand.strip() == '':
    print('Command name parameter is mandatory')
    sys.exit(2)

if (DeviceName.strip() != '') and ((AlternativeIPAddress.strip() != '') or (AlternativePort.strip() != '') or (AlternativeMACAddress.strip() != '') or (AlternativeTimeout != '')):
    print('Device name parameter can not be used in conjunction with IP Address/Port/MAC Address/Timeout parameters')
    sys.exit(2)

if (((AlternativeIPAddress.strip() != '') or (AlternativePort.strip() != '') or (AlternativeMACAddress.strip() != '') or (AlternativeTimeout.strip() != '')) and ((AlternativeIPAddress.strip() == '') or (AlternativePort.strip() == '') or (AlternativeMACAddress.strip() == '') or (AlternativeTimeout.strip() == ''))):
    print('IP Address, Port, MAC Address and Timeout parameters can not be used separately')
    sys.exit(2)

if DeviceName.strip() != '':
    if SettingsFile.has_section(DeviceName.strip()):
        if SettingsFile.has_option(DeviceName.strip(), 'IPAddress'):
            DeviceIPAddress = SettingsFile.get(DeviceName.strip(), 'IPAddress')
        else:
            DeviceIPAddress = ''

        if SettingsFile.has_option(DeviceName.strip(), 'Port'):
            DevicePort = SettingsFile.get(DeviceName.strip(), 'Port')
        else:
            DevicePort = ''

        if SettingsFile.has_option(DeviceName.strip(), 'MACAddress'):
            DeviceMACAddress = SettingsFile.get(DeviceName.strip(), 'MACAddress')
        else:
            DeviceMACAddress = ''

        if SettingsFile.has_option(DeviceName.strip(), 'Timeout'):
            DeviceTimeout = SettingsFile.get(DeviceName.strip(), 'Timeout')
        else:
            DeviceTimeout = ''        
    else:
        print('Device does not exist in BlackBeanControl.ini')
        sys.exit(2)

if (DeviceName.strip() != '') and (DeviceIPAddress.strip() == ''):
    print('IP address must exist in BlackBeanControl.ini for the selected device')
    sys.exit(2)

if (DeviceName.strip() != '') and (DevicePort.strip() == ''):
    print('Port must exist in BlackBeanControl.ini for the selected device')
    sys.exit(2)

if (DeviceName.strip() != '') and (DeviceMACAddress.strip() == ''):
    print('MAC address must exist in BlackBeanControl.ini for the selected device')
    sys.exit(2)

if (DeviceName.strip() != '') and (DeviceTimeout.strip() == ''):
    print('Timeout must exist in BlackBeanControl.ini for the selected device')
    sys.exit(2)    

if DeviceName.strip() != '':
    RealIPAddress = DeviceIPAddress.strip()
elif AlternativeIPAddress.strip() != '':
    RealIPAddress = AlternativeIPAddress.strip()
else:
    RealIPAddress = Settings.IPAddress

if RealIPAddress.strip() == '':
    print('IP address must exist in BlackBeanControl.ini or it should be entered as a command line parameter')
    sys.exit(2)

if DeviceName.strip() != '':
    RealPort = DevicePort.strip()
elif AlternativePort.strip() != '':
    RealPort = AlternativePort.strip()
else:
    RealPort = Settings.Port

if RealPort.strip() == '':
    print('Port must exist in BlackBeanControl.ini or it should be entered as a command line parameter')
    sys.exit(2)
else:
    RealPort = int(RealPort.strip())

if DeviceName.strip() != '':
    RealMACAddress = DeviceMACAddress.strip()
elif AlternativeMACAddress.strip() != '':
    RealMACAddress = AlternativeMACAddress.strip()
else:
    RealMACAddress = Settings.MACAddress

if RealMACAddress.strip() == '':
    print('MAC address must exist in BlackBeanControl.ini or it should be entered as a command line parameter')
    sys.exit(2)
else:
    RealMACAddress = netaddr.EUI(RealMACAddress)

if DeviceName.strip() != '':
    RealTimeout = DeviceTimeout.strip()
elif AlternativeTimeout.strip() != '':
    RealTimeout = AlternativeTimeout.strip()
else:
    RealTimeout = Settings.Timeout

if RealTimeout.strip() == '':
    print('Timeout must exist in BlackBeanControl.ini or it should be entered as a command line parameter')
    sys.exit(2)
else:
    RealTimeout = int(RealTimeout.strip())    

RM3Device = broadlink.rm((RealIPAddress, RealPort), RealMACAddress)
RM3Device.auth()

RM3Key = RM3Device.key
RM3IV = RM3Device.iv

if SettingsFile.has_option('Commands', SentCommand):
    CommandFromSettings = SettingsFile.get('Commands', SentCommand)
else:
    CommandFromSettings = ''

if CommandFromSettings.strip() != '':
    DecodedCommand = binascii.unhexlify(CommandFromSettings)

    AESEncryption = AES.new(str(RM3Key), AES.MODE_CBC, str(RM3IV))
    EncodedCommand = AESEncryption.encrypt(str(DecodedCommand))
    
    FinalCommand = EncodedCommand[0x04:]    
    RM3Device.send_data(FinalCommand)
else:
    RM3Device.enter_learning()
    time.sleep(RealTimeout)
    LearnedCommand = RM3Device.check_data()

    if LearnedCommand is None:
        print('Command not received')
        sys.exit()

    AdditionalData = bytearray([0x00, 0x00, 0x00, 0x00])    
    FinalCommand = AdditionalData + LearnedCommand

    AESEncryption = AES.new(str(RM3Key), AES.MODE_CBC, str(RM3IV))
    DecodedCommand = binascii.hexlify(AESEncryption.decrypt(str(FinalCommand)))

    BlackBeanControlIniFile = open(path.join(Settings.ApplicationDir, 'BlackBeanControl.ini'), 'w')    
    SettingsFile.set('Commands', SentCommand, DecodedCommand)
    SettingsFile.write(BlackBeanControlIniFile)
    BlackBeanControlIniFile.close()
    
