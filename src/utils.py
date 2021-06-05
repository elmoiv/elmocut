from subprocess import check_output, CalledProcessError
from socket import socket, getfqdn, gethostbyname
from threading import Thread
from scapy.all import conf
from manuf import manuf

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

def get_my_ip():
    """
    Try to extract ip of this device
    If fails: return localhost
    """
    try:
        return gethostbyname(getfqdn())
    except IndexError:
        return '127.0.0.1'

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

def is_connected():
    """
    Checks if there are any IPs in Default Gateway sections
    """
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