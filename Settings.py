import configparser
from os import path

ApplicationDir = path.dirname(path.abspath(__file__))
BlackBeanControlSettings = path.join(ApplicationDir, 'BlackBeanControl.ini')

Settings = configparser.ConfigParser()
Settings.read(BlackBeanControlSettings)

IPAddress = Settings.get('General', 'IPAddress')
Port = Settings.get('General', 'Port')
MACAddress = Settings.get('General', 'MACAddress')
Timeout = Settings.get('General', 'Timeout')
