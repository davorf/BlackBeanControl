import socket, configparser
import sys, getopt
import Settings

SettingsFile = configparser.ConfigParser()
SettingsFile.read(Settings.BlackBeanControlSettings)

SentCommand = ''
AlternativeIPAddress = ''
AlternativePort = ''

try:
    Options, args = getopt.getopt(sys.argv[1:], 'c:iph', ['command=','ipaddress=','port=','help'])
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

if AlternativeIPAddress.strip() != '':
    RealIPAddress = AlternativeIPAddress.strip()
else:
    RealIPAddress = Settings.IPAddress

if AlternativePort.strip() != '':
    RealPort = AlternativePort.strip()
else:
    RealPort = Settings.Port

RealCommand = SettingsFile.get('Commands', SentCommand)
        
RMSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

UDPData = bytearray.fromhex(Settings.DummyCommand)
RMSocket.connect((RealIPAddress, int(RealPort)))
RMSocket.send(UDPData)

UDPData = bytearray.fromhex(RealCommand)
RMSocket.connect((RealIPAddress, int(RealPort)))
RMSocket.send(UDPData)
 
RMSocket.close()
