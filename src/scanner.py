from utils import get_vendor, good_mac, get_my_ip, threaded
from scapy.all import Ether, arping, conf, get_if_addr
from os import system, popen
from time import sleep
from re import findall

class Scanner():
    def __init__(self):
        self.device_count = 24
        self.__ping_done = 0
        self.devices = []
        self.old_ips = {}
        self.router = {}
        self.ips = []
        self.me = {}
        self.qt_progress_signal = int
        self.qt_log_signal = print
    
    def init(self):
        """
        Intializing Scanner
        """
        self.router_ip = conf.route.route("0.0.0.0")[2]
        self.router_mac = 'FF:FF:FF:FF:FF:FF'

        self.my_ip = get_my_ip()
        self.my_mac = good_mac(Ether().src)
        
        self.ips = [
            f'{self.router_ip.rsplit(".", 1)[0]}.{i}'
                for i in range(self.device_count)
        ]

        self.add_me()
        self.add_router()
    
    def flush_arp(self):
        """
        Flush ARP cache
        """
        system('arp -d *')

    def add_me(self):
        """
        Get My info and append to self.devices
        """
        self.me = {
            'ip':       self.my_ip,
            'mac':      self.my_mac,
            'vendor':   get_vendor(self.my_mac),
            'type':     'Me',
            'admin':    True
        }
        
        self.devices.insert(0, self.me)

    def add_router(self):
        """
        Get Gateway info and append to self.devices
        """
        self.router = {
            'ip':       self.router_ip,
            'mac':      good_mac(self.router_mac),
            'vendor':   get_vendor(self.router_mac),
            'type':     'Router',
            'admin':    True
        }

        self.devices.insert(0, self.router)

    def devices_appender(self, scan_result):
        """
        Append scan results to self.devices
        """
        self.devices = []
        unique = []

        # Sort by last part of ip xxx.xxx.x.y
        scan_result = sorted(
            scan_result,
            key=lambda i:int(i[0].split('.')[-1])
        )
        
        for ip, mac in scan_result:
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
                    'type':   'User',
                    'admin':  False
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
    
    def arping_cache(self):
        """
        Showing system arp cache after pinging
        """
        self.init()

        scan_result = popen('arp -a').read()
        clean_result = findall(r'([0-9.]+)\s+([0-9a-f-]+)\s+dynamic', scan_result)
        
        self.devices_appender(clean_result)
    
    def arp_scan(self):
        """
        Scan using Scapy arping method 
        """
        self.init()

        scan_result = arping(f"{self.router_ip}/24", verbose=0, timeout=1)
        clean_result = [(i[1].psrc, i[1].src) for i in scan_result[0]]

        self.devices_appender(clean_result)

    def ping_scan(self):
        """
        Ping all devices at once [CPU Killing function]
           (All Threads will run at the same tine)
        """
        self.init()
        
        self.__ping_done = 0
        
        for ip in self.ips:
            self.ping_thread(ip)
        
        while self.__ping_done < self.device_count:
            # Add a sleep to overcome High CPU usage
            sleep(.01)
            self.qt_progress_signal(self.__ping_done)
        
        return True
    
    @threaded
    def ping_thread(self, ip):
        """
        Sub function for pinging
        """
        # Workaround for no verbose commands
        _ = popen(f'ping -n 1 {ip}').read()
        self.__ping_done += 1