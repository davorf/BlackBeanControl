#!python2

import broadlink, configparser
import sys, getopt
import time, binascii
import netaddr
import Settings
import string
from os import path
from Crypto.Cipher import AES

SettingsFile = configparser.ConfigParser()
SettingsFile.optionxform = str
SettingsFile.read(Settings.BlackBeanControlSettings)

SentCommand = ''
ReKeyCommand = False
RealCommand = ''
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
    Options, args = getopt.getopt(sys.argv[1:], 'c:n:s:d:r:i:p:m:t:h', ['command=', 'command=', 'command=','device=','rekey=','ipaddress=','port=','macaddress=','timeout=','help'])
except getopt.GetoptError:
    print('BlackBeanControl.py -c <Command name> [-d <Device name>] [-i <IP Address>] [-p <Port>] [-m <MAC Address>] [-t <Timeout>] [-r <Re-Key Command>]')
    sys.exit(2)

for Option, Argument in Options:
    if Option in ('-h', '--help'):
        print('BlackBeanControl.py -c <Command name> [-d <Device name>] [-i <IP Address>] [-p <Port>] [-m <MAC Address>] [-t <Timeout> [-r <Re-Key Command>]')
        print('To control NEC     BlackBeanControl.py -n <Command HEX 4 bytes> [-d <Device name>] [-i <IP Address>] [-p <Port>] [-m <MAC Address>] [-t <Timeout>')
        print('To control Samsung BlackBeanControl.py -n <Command HEX 6 bytes> [-d <Device name>] [-i <IP Address>] [-p <Port>] [-m <MAC Address>] [-t <Timeout>')
        sys.exit()
    elif Option in ('-c', '--command'):
        RealCommand = 'c'
        SentCommand = Argument
    elif Option in ('-n', '--nec'):
        RealCommand = 'n'
        SentCommand = Argument
    elif Option in ('-s', '--samsung'):
        RealCommand = 's'
        SentCommand = Argument
    elif Option in ('-d', '--device'):
        DeviceName = Argument
    elif Option in ('-r', '--rekey'):
        ReKeyCommand = True
        SentCommand = Argument
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

RM3Device = broadlink.rm((RealIPAddress, RealPort), RealMACAddress, RealTimeout)
RM3Device.auth()

if ReKeyCommand:
    if SettingsFile.has_option('Commands', SentCommand):
        CommandFromSettings = SettingsFile.get('Commands', SentCommand)

        if CommandFromSettings[0:4] != '2600':
            RM3Key = RM3Device.key
            RM3IV = RM3Device.iv

            DecodedCommand = binascii.unhexlify(CommandFromSettings)
            AESEncryption = AES.new(str(RM3Key), AES.MODE_CBC, str(RM3IV))
            EncodedCommand = AESEncryption.encrypt(str(DecodedCommand))
            FinalCommand = EncodedCommand[0x04:]
            EncodedCommand = FinalCommand.encode('hex')

            BlackBeanControlIniFile = open(path.join(Settings.ApplicationDir, 'BlackBeanControl.ini'), 'w')
            SettingsFile.set('Commands', SentCommand, EncodedCommand)
            SettingsFile.write(BlackBeanControlIniFile)
            BlackBeanControlIniFile.close()
            sys.exit()
        else:
            print("Command appears to already be re-keyed.")
            sys.exit(2)
    else:
        print("Command not found in ini file for re-keying.")
        sys.exit(2)

if RealCommand == 'n':
    if (len(SentCommand) <> 8) or (not all(c in string.hexdigits for c in SentCommand)):
        print('Command must be 4-byte hex number.')
        sys.exit(2)

    BinStr = "".join('%s' % bin(int(SentCommand[i: i + 2], 16))[2:].zfill(8)[::-1] for i in xrange(0, 7, 2))
    
    # start sequence + NEC start + bits + end pulse with long pause + end sequence
    EncodedCommand = '26002e01' + '00012b96' + "".join(('1440' if c == '1' else '1414') for c in BinStr) + '1400072a' + '000d05'
    
    RM3Device.send_data(EncodedCommand.decode('hex'))

    sys.exit()

if RealCommand == 's':
    if (len(SentCommand) <> 12) or (not all(c in string.hexdigits for c in SentCommand)):
        print('Command must be 6-byte hex number.')
        sys.exit(2)

    BinStr = "".join('%s' % bin(int(SentCommand[i: i + 2], 16))[2:].zfill(8)[::-1] for i in xrange(0, 11, 2))
    
    # start sequence + Samsung start + data + end pulse + (here the copy)Samsung start + data + end pulse with long pause + end sequence
    EncodedBinStr = "".join(('1434' if (c == '1') else '1414') for c in BinStr)
    EncodedCommand = '2600ca00' + '9494' + EncodedBinStr + '1494' + '9494' + EncodedBinStr + '1400072a' + '000d05'
 
    RM3Device.send_data(EncodedCommand.decode('hex'))
    sys.exit()


if SettingsFile.has_option('Commands', SentCommand):
    CommandFromSettings = SettingsFile.get('Commands', SentCommand)
else:
    CommandFromSettings = ''

if CommandFromSettings.strip() != '':
    DecodedCommand = CommandFromSettings.decode('hex')
    RM3Device.send_data(DecodedCommand)
else:
    RM3Device.enter_learning()
    time.sleep(RealTimeout)
    LearnedCommand = RM3Device.check_data()

    if LearnedCommand is None:
        print('Command not received')
        sys.exit()

    EncodedCommand = LearnedCommand.encode('hex')

    BlackBeanControlIniFile = open(path.join(Settings.ApplicationDir, 'BlackBeanControl.ini'), 'w')    
    SettingsFile.set('Commands', SentCommand, EncodedCommand)
    SettingsFile.write(BlackBeanControlIniFile)
    BlackBeanControlIniFile.close()
    
