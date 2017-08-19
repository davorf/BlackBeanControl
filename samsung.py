#!python2

import Settings
import copy
import string
import sys, getopt
import time, binascii
import netaddr
import broadlink, configparser
from os import path
from Crypto.Cipher import AES

def eq(cnst, val):
    return ((cnst * 1.2 > val) and ((cnst * 0.8) < val))
    
def BinDecode(sbin):
    if len(sbin) <> 48:
        print('bin length error. len=' + str(len(sbin)))
        return False

    xbin = 'x' + sbin
    BinArray = [xbin[i * 8: (i - 1) * 8: -1] for i in xrange(1, 7)]
#    BinArray = [sbin[7: -49: -1], sbin[15: 7: -1], sbin[23: 15: -1], sbin[31: 23: -1], sbin[39: 31: -1], sbin[47: 39: -1]] !!!
#    BinArray = [sbin[7: : -1], sbin[15: 7: -1], sbin[23: 15: -1], sbin[31: 23: -1], sbin[39: 31: -1], sbin[47: 39: -1]]
#    BinArray = [sbin[: 7: 1], sbin[7: 15: 1], sbin[15: 23: 1], sbin[23: 31: 1], sbin[31: 39: 1], sbin[39: 47: 1]]
    HexArray = ['%02X' % int(x, 2) for x in BinArray]         
    
    print('bin cmd' + "".join(' %s' % s for s in BinArray))
    print('hex cmd' + "".join(' %s' % s for s in HexArray))
    print('dec cmd' + ''.join(' %03d' % int(b, 2) for b in BinArray))
    return True;

SentCommand = ''

SettingsFile = configparser.ConfigParser()
SettingsFile.optionxform = str
SettingsFile.read(Settings.BlackBeanControlSettings)

try:
    Options, args = getopt.getopt(sys.argv[1:], 'd:e:p:n:h', ['command=', 'command=', 'command=', 'neccmd=', 'help'])
except getopt.GetoptError:
    print('Options error. Try -d for decode or -h for help. ')
    sys.exit(2)

MainCmd = '';
for Option, Argument in Options:
    if Option in ('-h', '--help'):
        print('Samsung48 IR protocol (NEC48-2) decoder/encoder.')
        print('Print command from ini file:')
        print('    samsung.py -p <Command name>')
        print('Decode:')
        print('    samsung.py -d <Command name>')
        print('Export as timing list:')
        print('    samsung.py -e <Command name>')
        print('Encode Samsung IR command:')
        print('    samsung.py -n <Samsung command in HEX>')
        sys.exit()
    elif Option in ('-p', '--print'):
        SentCommand = Argument
        MainCmd = 'p';
    elif Option in ('-d', '--decode'):
        SentCommand = Argument
        MainCmd = 'd';
    elif Option in ('-e', '--export'):
        SentCommand = Argument
        MainCmd = 'e';
    elif Option in ('-n', '--encode'):
        SentCommand = Argument
        MainCmd = 'n';

if SentCommand.strip() == '':
    print('Command name parameter is mandatory')
    sys.exit(2)

if SettingsFile.has_option('Commands', SentCommand):
    CommandFromSettings = SettingsFile.get('Commands', SentCommand)
else:
    CommandFromSettings = ''

if (MainCmd in ['d', 'e', 'p']) and (CommandFromSettings.strip() != ''):
    DecodedCommand = CommandFromSettings.decode('hex')

    # print command
    if MainCmd == 'p':
        print(CommandFromSettings)
        sys.exit(0)
    
    #'d','e' commands
    Intv = '';
    LenArray = [];
    for s in DecodedCommand:
        Intv = Intv + s;
        # EOF
        if Intv == '\x00\x0d\x05':
#            print("eof")
            break;
        # 1-byte or 3-byte values. 3-byte values starts with 0x00
        if (Intv[0] <> '\x00') or (Intv[0] == '\x00' and len(Intv) >= 3):
            IntI = int(Intv.encode('hex'), 16) * 1000 * 269 / 8192
            LenArray.append(IntI)
#            print(IntI)
            Intv = ''

    print('Array length ' + str(len(LenArray)))
    if MainCmd == 'e':
        print(''.join((' +' if (ind % 2 == 0) else ' -') + '%d' % i for ind,i in enumerate(LenArray)))
        sys.exit(0);

    DecodeState = ['init', '1bwait', 'pulse', 'pause', 'stop']
    decoding = DecodeState[0]

    BinStr = '';
    for indx in range(0, len(LenArray) - 1):
        if ((indx < len(LenArray) - 3) and eq(4500, LenArray[indx]) and eq(4500, LenArray[indx + 1]) and (300 < LenArray[indx + 2] < 1000)):
            if BinStr <> '':
                BinDecode(BinStr)
            BinStr = ''
            decoding = '1bwait'
            print('--------------------------------------------')
            print('sequence started at indx:' + str(indx) + ' ' + str(LenArray[indx]))
            continue

        if decoding == '1bwait':
            decoding = 'pulse'
            continue

        # 550-550 = 0; 550-1450 = 1 in microseconds
		# decoder setiings - 0.3-1ms pulse and '0', 1-2ms - '1', else - error
        if decoding == 'pulse':
            if 300 < LenArray[indx] < 900:
                decoding = 'pause'
                continue
            else:
                print('error bit1 length=' + str(LenArray[indx]) + ' indx=' + str(indx))
                decoding = 'init'
                continue

        if decoding == 'pause':
            if 300 < LenArray[indx] < 1000:
                BinStr = BinStr + '0'
            elif 1000 < LenArray[indx] < 2000:
                BinStr = BinStr + '1'
            else:
                print('error bit2 length=' + str(LenArray[indx]) + ' indx=' + str(indx))
                decoding = 'init'
                continue
            decoding = 'pulse'

        if (decoding == 'init' and BinStr <> '') or (indx == len(LenArray) - 2 and BinStr <> ''):
            print('decoded ' + BinStr)
            BinDecode(BinStr)
            BinStr = ''

    if BinStr <> '':
        BinDecode(BinStr)
        
    sys.exit(0)

if (MainCmd in ['n']) and (SentCommand.strip() != ''):
    if (len(SentCommand) <> 12) or (not all(c in string.hexdigits for c in SentCommand)):
        print('Command must be 6-byte hex number.')
        sys.exit(2)

    print('hex command=' + SentCommand)
    
    BinArray = [bin(int(SentCommand[i: i + 2], 16))[2:].zfill(8)[::-1] for i in xrange(0, 11, 2)];
    BinStr = "".join('%s' % s for s in BinArray)
    print ('bin command=' + BinStr)
    
    # start sequence + Samsung start + data + end pulse + (here the copy)Samsung start + data + end pulse with long pause + end sequence
    EncodedBinStr = "".join(('1434' if (c == '1') else '1414') for c in BinStr)
    Cmd = '2600ca00' + '9494' + EncodedBinStr + '1494' + '9494' + EncodedBinStr + '1400072a' + '000d05'
    
    print(Cmd)
    sys.exit(0)
