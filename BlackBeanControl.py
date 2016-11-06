#!python2

import broadlink, configparser
import sys, getopt
import os, time
import binascii
import Settings
import netaddr
from os import path
from Crypto.Cipher import AES

SettingsFile = configparser.ConfigParser()
SettingsFile.optionxform = str
SettingsFile.read(Settings.BlackBeanControlSettings)

SentCommand = ''
AlternativeIPAddress = ''
AlternativePort = ''
AlternativeMACAddress = ''

try:
    Options, args = getopt.getopt(sys.argv[1:], 'c:i:p:m:h', ['command=','ipaddress=','port=', 'macaddress=','help'])
except getopt.GetoptError:
    print('BlackBeanControl.py -c <Command name> [-i <IP Address>] [-p <Port>] [-m <MAC Address>]')
    sys.exit(2)

for Option, Argument in Options:
    if Option in ('-h', '--help'):
        print('BlackBeanControl.py -c <Command name> [-i <IP Address>] [-p <Port>] [-m <MAC Address>]')
        sys.exit()
    elif Option in ('-c', '--command'):
        SentCommand = Argument
    elif Option in ('-i', '--ipaddress'):
        AlternativeIPAddress = Argument
    elif Option in ('-p', '--port'):
        AlternativePort = Argument
    elif Option in ('-m', '--macaddress'):
        AlternativeMACAddress = Argument

if SentCommand.strip() == '':
    print('Command name parameter is mandatory')
    sys.exit(2)

if AlternativeIPAddress.strip() != '':
    RealIPAddress = AlternativeIPAddress.strip()
else:
    RealIPAddress = Settings.IPAddress

if RealIPAddress.strip() == '':
    print('IP address must exist in BlackBeanControl.ini or it should be entered as a command line parameter')
    sys.exit(2)

if AlternativePort.strip() != '':
    RealPort = AlternativePort.strip()
else:
    RealPort = Settings.Port

if RealPort.strip() == '':
    print('Port must exist in BlackBeanControl.ini or it should be entered as a command line parameter')
    sys.exit(2)
else:
    RealPort = int(RealPort.strip())

if AlternativeMACAddress.strip() != '':
    RealMACAddress = AlternativeMACAddress.strip()
else:
    RealMACAddress = Settings.MACAddress

if RealMACAddress.strip() == '':
    print('MAC address must exist in BlackBeanControl.ini or it should be entered as a command line parameter')
    sys.exit(2)
else:
    RealMACAddress = netaddr.EUI(RealMACAddress)

RM3Device = broadlink.device((RealIPAddress, RealPort), RealMACAddress)
RM3Device.auth()

RM3Key = RM3Device.key
RM3IV = RM3Device.iv

TimeoutFromSettings = Settings.Timeout

if TimeoutFromSettings.strip() == '':
    RealTimout = 30
else:
    RealTimeout = int(TimeoutFromSettings.strip())

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
    
