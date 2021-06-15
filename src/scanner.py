from utils import get_vendor, good_mac, get_my_ip, threaded, terminal, get_default_iface
from concurrent.futures.thread import ThreadPoolExecutor
from scapy.all import Ether, arping, conf, get_if_addr
from time import sleep
from re import findall

from constants import *

class Scanner():
    def __init__(self):
        self.iface = get_default_iface()
        self.device_count = 25
        self.max_threads = 8
        self.__ping_done = 0
        self.devices = []
        self.old_ips = {}
        self.router = {}
        self.ips = []
        self.me = {}
        self.perfix = None
        self.qt_progress_signal = int
        self.qt_log_signal = print
    
    def generate_ips(self):
        self.ips = [f'{self.perfix}.{i}' for i in range(1, self.device_count)]

    def init(self):
        """
        Intializing Scanner
        """
        # Refresh Scapy
        conf.route.resync()

        self.router_ip = conf.route.route("0.0.0.0")[2]
        self.router_mac = GLOBAL_MAC

        self.my_ip = self.iface.ip
        self.my_mac = good_mac(self.iface.mac)
        
        self.perfix = self.my_ip.rsplit(".", 1)[0]
        self.generate_ips()

        self.add_me()
        self.add_router()
    
    def flush_arp(self):
        """
        Flush ARP cache
        """
        arp_cmd = terminal('arp -d *')
        # Fix: Some systems has older versions of arp.exe
        # We use netsh instead
        if 'The parameter is incorrect' in arp_cmd:
            terminal('netsh interface ip delete arpcache')

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
            if mac == self.my_mac or mac in unique:
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
        # Correct scan result when working with specific interface
        scan_result = terminal('arp -a').replace('\n', '-') + '-'
        iface_specific = ' '.join(findall(rf'Interface: {self.my_ip} (.*)--', scan_result))

        clean_result = findall(rf'({self.perfix}\.\d+)\s+([0-9a-f-]+)\s+dynamic', iface_specific)
        
        self.devices_appender(clean_result)
    
    def arp_scan(self):
        """
        Scan using Scapy arping method 
        """
        if self.router_mac == GLOBAL_MAC:
            self.init()

        self.generate_ips()
        scan_result = arping(
            f"{self.router_ip}/24",
            iface=self.iface.name,
            verbose=0,
            timeout=1
        )
        clean_result = [(i[1].psrc, i[1].src) for i in scan_result[0]]

        self.devices_appender(clean_result)

    def ping_scan(self):
        """
        Ping all devices at once [CPU Killing function]
           (All Threads will run at the same tine)
        """
        self.__ping_done = 0

        if self.router_mac == GLOBAL_MAC:
            self.init()
        
        self.generate_ips()
        self.ping_thread_pool()
        
        while self.__ping_done < self.device_count - 1:
            # Add a sleep to overcome High CPU usage
            sleep(.01)
            self.qt_progress_signal(self.__ping_done)
        
        return True
    
    @threaded
    def ping_thread_pool(self):
        """
        Control maximum threads running at once
        """
        with ThreadPoolExecutor(self.max_threads) as executor:
            for ip in self.ips:
                executor.submit(self.ping, ip)

    def ping(self, ip):
        """
        Ping a specific ip with native command "ping -n"
        """
        terminal(f'ping -n 1 {ip}', decode=False)
        self.__ping_done += 1