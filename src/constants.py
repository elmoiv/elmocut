from os import path, environ
from models.device import Device
from enums import DeviceType

OLD_DOCUMENTS_PATH = path.join(environ['USERPROFILE'], 'Documents', 'elmocut')
DOCUMENTS_PATH = path.join(environ['APPDATA'], 'elmocut')

OLD_SETTINGS_PATH = path.join(OLD_DOCUMENTS_PATH, 'elmocut.json')
SETTINGS_PATH = path.join(DOCUMENTS_PATH, 'elmocut.json')

TABLE_HEADER_LABELS = ['IP Address', 'MAC Address', 'Vendor', 'Type', 'Nickname']

NPCAP_URL = 'https://nmap.org/npcap/dist/npcap-1.50.exe'

NPCAP_PATH = 'C:\\Windows\\SysWOW64\\Npcap'

GLOBAL_MAC = 'FF:FF:FF:FF:FF:FF'

DUMMY_ROUTER = Device(
            ip = '192.168.1.1',
            mac = GLOBAL_MAC,
            vendor = 'NONE',
            dtype = DeviceType.ROUTER,
            name = '-',
            admin = True
        )

DUMMY_IFACE = {'name': 'NULL', 'mac': GLOBAL_MAC, 'guid': 'NULL', 'ips': ['0.0.0.0']}

HKEY_AUTOSTART_PATH = 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run'

SETTINGS_KEYS = ['dark', 'count', 'autostart', 'minimized', 'remember', 'killed', 'autoupdate', 'threads', 'iface', 'nicknames']

SETTINGS_VALS = [True, 25, False, True, False, [], True, 12, '', {}]

# Terminal commands
CMD_PING_DEVICE = 'ping -n 1 {}'.format
CMD_ARP_CACHE = 'arp -a -N {} | findstr dynamic'.format
CMD_ARP_CACHE_FLUSH = 'arp -d *'
CMD_ARP_CACHE_FLUSH_NEW = 'netsh interface ip delete arpcache'

VERSION = '1.0.7'