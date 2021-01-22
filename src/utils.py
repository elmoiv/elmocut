from threading import Thread
from os import popen, system
from scapy.all import conf
from manuf import manuf

p = manuf.MacParser()

def threaded(fn):
    """
    Thread wrapper function (decorator)
    """
    def run(*k, **kw):
        t = Thread(target=fn, args=k, kwargs=kw)
        t.start()
        return t
    return run

def get_vendor(mac):
    """
    Get vendor from manuf wireshark mac database
    """
    return p.get_manuf(mac) or 'None'

def good_mac(mac):
    """
    Convert dash separated MAC to colon separated
    """
    return mac.upper().replace('-', ':')

def is_connected():
    """
    Check if interface is connected to router
    """
    # Checks if there are any IPs in Default Gateway sections
    # We only need to make sure we are connected to router
    output = popen(
        'ipconfig | findstr "Default Gateway"'
        ).read().replace('.', '')
    return bool([i for i in output if i.isdigit()])

def get_my_ip():
    """
    Try to extract ip of this device
    If fails: return localhost
    """
    try:
        return [x[4] for x in conf.route.routes if x[2] != '0.0.0.0'][0]
    except IndexError:
        return '127.0.0.1'

def goto(url):
    system(f'start "" "{url}"')