from scapy.all import conf, get_if_list, get_windows_if_list, get_if_hwaddr
from subprocess import check_output, CalledProcessError
from socket import socket
from threading import Thread
from manuf import manuf

from networking.ifaces import NetFace
from constants import *

p = manuf.MacParser()

def terminal(command, shell=True, decode=True):
    """
    Terminal commands via Subprocess
    """
    try:
        cmd = check_output(command, shell=shell)
        return cmd.decode() if decode else None
    except CalledProcessError:
        return None
    except UnicodeDecodeError:
        return str(cmd)

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

def get_my_ip(iface_name):
    """
    Get Gateway IP if connected else None
    """
    response = terminal('netsh interface ip show address '
                      f'"{iface_name}" | findstr "IP"')
    return response.split()[-1] if response else '127.0.0.1'

def get_gateway_ip(iface_name):
    """
    Get Gateway IP if connected else None
    """
    response = terminal('netsh interface ip show address '
                      f'"{iface_name}" | findstr /i default')
    return response.split()[-1] if response else '0.0.0.0'

def get_gateway_mac(iface_ip, router_ip):
    response = terminal(f'arp -a {router_ip} -N {iface_ip} | findstr "dynamic static"')
    try:
        return good_mac(response.split()[1])
    except:
        return GLOBAL_MAC

def goto(url):
    """
    Open url in default browser
    """
    terminal(f'start "" "{url}"')

def check_connection(func):
    """
    Connection checker decorator
    """
    def wrapper(*args, **kargs):
        if is_connected():
            # args[0] == "self" in ElmoCut class
            return func(args[0])
    return wrapper

def get_ifaces():
    """
    Get current working interfaces
    """
    conf.route.resync()
    pcap = [net.split('_')[-1] for net in get_if_list()]
    for iface in get_windows_if_list():
        if iface['guid'] in pcap: 
            yield NetFace(iface)

def get_default_iface():
    """
    Get default pcap interface
    """
    for iface in get_ifaces():
        if iface.guid in str(conf.iface):
            return iface
    return NetFace(DUMMY_IFACE)

def get_iface_by_name(name):
    """
    Return interface given its name
    """
    for iface in get_ifaces():
        if iface.name == name:
            return iface
    return get_default_iface()

def is_connected(current_iface=get_default_iface()):
    """
    Checks if there are any IPs in Default Gateway sections
    """
    # print(current_iface)
    if current_iface.name == 'NULL':
        return False

    ipconfig_output = terminal('ipconfig | findstr /i gateway')
    if ipconfig_output != None:
        return any(i.isdigit() for i in ipconfig_output)

    # Alternative way if ipconfig has error in some systems
    ## Slower than ipconfig workaround
    try:
        socket().connect(('8.8.8.8', 53))
        return True
    except:
        return False
