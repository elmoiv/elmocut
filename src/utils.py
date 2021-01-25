from subprocess import check_output, CalledProcessError
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
    output = terminal('ipconfig | findstr "Default Gateway"')
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
    """
    Open url in default browser
    """
    terminal(f'start "" "{url}"')
