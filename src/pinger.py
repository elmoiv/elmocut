from utils import threaded
from os import popen
from time import sleep

class Pinger:
    def __init__(self):
        self.IPs = []
        self.ping_done = []
        self.device_count = 24
    
    def threaded_pinging(self):
        '''
        Ping all devices at once [CPU Killing function]
           (All Threads will run at the same tine)
        '''
        self.ping_done = []
        for ip in self.IPs:
            self.ping_thread(ip)
    
    @threaded
    def ping_thread(self, ip):
        '''
        Sub function for pinging
        '''
        # Workaround for no verbose commands
        _ = popen(f'ping -n 1 {ip}').read()
        self.ping_done.append(1)
    
    def pinging_watcher(self, qt_prgoress_signal=bool):
        '''
        Watching pinging thread to check if done
        '''
        while len(self.ping_done) < self.device_count:
            # Add a sleep to overcome High CPU usage
            sleep(.01)
            qt_prgoress_signal(len(self.ping_done))
        return True
