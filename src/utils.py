from threading import Thread
from scapy.all import conf
from manuf import manuf
import socket

p = manuf.MacParser()

def threaded(fn):
    '''
    Thread wrapper function (decorator)
    '''
    def run(*k, **kw):
        t = Thread(target=fn, args=k, kwargs=kw)
        t.start()
        return t
    return run

def get_vendor(mac):
    '''
    Get vendor from manuf wireshark mac database
    '''
    return p.get_manuf(mac) or 'None'

def good_mac(mac):
    '''
    Convert dash separated MAC to colon separated
    '''
    return mac.upper().replace('-', ':')

def is_connected(host="8.8.8.8", port=53, timeout=3):
    '''
    Check if connected to internet
    '''
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
            ).connect((host, port))
    except socket.error:
        return False
    return True

def get_my_ip():
    '''
    Try to extract ip of this device
    If fails: return localhost
    '''
    try:
        return [x[4] for x in conf.route.routes if x[2] != '0.0.0.0'][0]
    except:
        return '127.0.0.1'
