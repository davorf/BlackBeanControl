import socket, configparser
import sys, getopt
import os, binascii
import Settings

SettingsFile = configparser.ConfigParser()
SettingsFile.read(Settings.BlackBeanControlSettings)

SentCommand = ''
AlternativeIPAddress = ''
AlternativePort = ''

try:
    Options, args = getopt.getopt(sys.argv[1:], 'c:i:p:h', ['command=','ipaddress=','port=','help'])
except getopt.GetoptError:
    print('BlackBeanControl.py -c <Command name> [-i <IP Address>] [-p <Port>]')
    sys.exit(2)

for Option, Argument in Options:
    if Option in ('-h', '--help'):
        print('BlackBeanControl.py -c <Command name> [-i <IP Address>] [-p <Port>]')
        sys.exit()
    elif Option in ('-c', '--command'):
        SentCommand = Argument
    elif Option in ('-i', '--ipaddress'):
        AlternativeIPAddress = Argument
    elif Option in ('-p', '--port'):
        AlternativePort = Argument

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

if SettingsFile.has_option('Commands', SentCommand):
    CommandFromSettings = SettingsFile.get('Commands', SentCommand)
else:
    CommandFromSettings = ''

if CommandFromSettings.strip() != '':
    try:
        FirstRandomPart = binascii.b2a_hex(os.urandom(2))
        SecondRandomPart = binascii.b2a_hex(os.urandom(2))
        CommandToSend = CommandFromSettings[0:64] + FirstRandomPart.decode('utf-8') + CommandFromSettings[68:80] + SecondRandomPart.decode('utf-8') + CommandFromSettings[84:432]
                
        RMSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

        try:
            UDPData = bytearray.fromhex(CommandToSend)
        except:
            print('An error occured while trying to convert UDP payload to byte array')
            sys.exit(1)
            
        RMSocket.connect((RealIPAddress, int(RealPort)))
        RMSocket.send(UDPData)
         
        RMSocket.close()
    except socket.error as SocketErrorMessage:
        print('An error occured while trying to send UDP payload. Original message: %s' % SocketErrorMessage)
        sys.exit(1)
else:
    print('Command not found in BlackBeanControl.ini')
    
