from utils import get_vendor, good_mac, get_my_ip, threaded
from pinger import Pinger
from scapy.all import Ether, arping, conf, get_if_addr
from os import system, popen
from re import findall

class Scanner(Pinger):
    def __init__(self):
        super().__init__()
        self.devices = []
        self.old_ips = {}
        self.router = {}
        self.me = {}
    
    def init(self):
        '''
        Intializing Scanner
        '''
        self.router_ip = conf.route.route("0.0.0.0")[2]
        self.router_mac = 'FF:FF:FF:FF:FF:FF'

        self.my_ip = get_my_ip()
        self.my_mac = good_mac(Ether().src)
        
        self.IPs = [
            f'{self.router_ip.rsplit(".", 1)[0]}.{i}'
                for i in range(self.device_count)
        ]

        self.add_me()
        self.add_router()
    
    def flush_arp(self):
        '''
        Flush ARP cache
        '''
        system('arp -d *')

    def add_me(self):
        '''
        Get My info and append to self.devices
        '''
        self.me = {
            'ip': self.my_ip,
            'mac': self.my_mac,
            'vendor': get_vendor(self.my_mac),
            'type': 'Me'
        }
        
        self.devices.insert(0, self.me)

    def add_router(self):
        '''
        Get Gateway info and append to self.devices
        '''
        self.router = {
            'ip': self.router_ip,
            'mac': good_mac(self.router_mac),
            'vendor': get_vendor(self.router_mac),
            'type': 'Router'
        }

        self.devices.insert(0, self.router)

    def devices_appender(self, scan_result):
        '''
        Append scan results to self.devices
        '''
        self.devices = []
        unique = []

        for ip, mac in sorted(set(scan_result)):
            mac = good_mac(mac)

            # Store gateway
            if ip == self.router_ip:
                self.router_mac = mac
                continue
            
            # Skip me or duplicated devices
            if ip == self.my_ip or mac in unique:
                continue
            
            # update same device with new ip
            if self.old_ips.get(mac, ip) != ip:
                self.old_ips[mac] = ip
                unique.append(mac)

            self.devices.append(
                {
                    'ip':     ip,
                    'mac':    good_mac(mac),
                    'vendor': get_vendor(mac),
                    'type':   'User'
                }
            )
        
        # Remove device with old ip
        for device in self.devices[:]:
            mac, ip = device['mac'], device['ip']
            if self.old_ips.get(mac, ip) != ip:
                self.devices.remove(device)
        
        # Re-create devices old ips dict
        self.old_ips = {d['mac']: d['ip'] for d in self.devices}

        self.add_me()
        self.add_router()

        # Clear arp cache to avoid duplicates next time
        if unique:
            self.flush_arp()

    def scan(self):
        '''
        Scan using Scapy arping method 
        '''
        self.init()

        scan_result = arping(f"{self.router_ip}/24", verbose=0)
        clean_result = [(i[1].psrc, i[1].src) for i in scan_result[0]]
        
        self.devices_appender(clean_result)
    
    def arping_cache(self):
        '''
        Showing system arp cache after pinging
        '''
        self.init()

        scan_result = popen('arp -a').read()
        clean_result = findall(r'([0-9.]+)\s+([0-9a-f-]+)\s+dynamic', scan_result)
        
        self.devices_appender(clean_result)