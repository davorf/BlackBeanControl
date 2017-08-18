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
    return ((cnst * 1.3 > val) and ((cnst * 0.7) < val))
    
def BinDecode(sbin):
    if len(sbin) <> 32:
        print('bin length error. len=' + str(len(sbin)))
        return False

    BinArray = [sbin[7: : -1], sbin[15: 7: -1], sbin[23: 15: -1], sbin[31: 23: -1]]
    HexArray = []
    HexArray[:] = ['%02X' % int(x, 2) for x in BinArray]         
    
    BinStr = "".join(' %s' % s for s in BinArray)
    HexStr = "".join(' %s' % s for s in HexArray)
    print('bin cmd' + BinStr)
    print('hex cmd' + HexStr)
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
        print('NEC IR protocol decoder/encoder.')
        print('Print commanf from ini file:')
        print('    nec.py -p <Command name>')
        print('Decode:')
        print('    nec.py -d <Command name>')
        print('Export as timing list:')
        print('    nec.py -e <Command name>')
        print('Encode NEC IR command:')
        print('    nec.py -n <NEC command in HEX>')
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
    for indx in range(0, len(LenArray) - 2):
        if (eq(9000, LenArray[indx]) and eq(4500, LenArray[indx + 1])):
            decoding = '1bwait'
            print('--------------------------------------------')
            print('sequence started at indx:' + str(indx) + ' ' + str(LenArray[indx]))
            continue

        if decoding == '1bwait':
            decoding = 'pulse'
            continue

        # 562-562 = 0; 562-1688 = 1 in microseconds
        if decoding == 'pulse':
            if eq(700, LenArray[indx]):
                decoding = 'pause'
                continue
            else:
                print('error bit1 length=' + str(LenArray[indx]) + ' indx=' + str(indx))
                decoding = 'init'
                continue

        if decoding == 'pause':
            if eq(700, LenArray[indx]):
                BinStr = BinStr + '0'
            elif eq(1800, LenArray[indx]):
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
    if (len(SentCommand) <> 8) or (not all(c in string.hexdigits for c in SentCommand)):
        print('Command must be 4-byte hex number.')
        sys.exit(2)

    print('hex command=' + SentCommand)
    
    BinArray = [];
    BinArray[:] = [bin(int(SentCommand[i: i + 2], 16))[2:].zfill(8)[::-1] for i in xrange(0, 7, 2)];
    BinStr = "".join('%s' % s for s in BinArray)
    print ('bin command=' + BinStr)
    
    # start sequence + NEC start + bits + end pulse with long pause + end sequence
    Cmd = '26002e01' + '00012b96' + "".join(('1440' if (c == '1') else '1414') for c in BinStr) + '1400072a' + '000d05'
    
    print(Cmd)
    sys.exit(0)
