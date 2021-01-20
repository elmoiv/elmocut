from win32gui import EnumWindows, GetWindowText, ShowWindow
from threading import Thread
from os import popen, path
from scapy.all import conf
from manuf import manuf
import socket

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

def is_connected(host="8.8.8.8", port=53, timeout=3):
    """
    Check if connected to internet
    """
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
    """
    Try to extract ip of this device
    If fails: return localhost
    """
    try:
        return [x[4] for x in conf.route.routes if x[2] != '0.0.0.0'][0]
    except:
        return '127.0.0.1'

def npcap_exists():
    """
    Check for Npcap driver
    """
    return path.exists(r'C:\Windows\SysWOW64\Npcap')

def duplicate_elmocut():
    """
    Check if there is more than 1 instance of elmoCut.exe
    """
    tasklist = popen('tasklist').read()
    return tasklist.lower().count('elmocut.exe') > 1

def bring_elmocut_tofront():
    # Inspired from:
    # https://github.com/iwalton3/plex-mpv-shim/blob/master/plex_mpv_shim/win_utils.py
    """
    Bring elmoCut window to front
    """
    top_windows = {}
    
    # Get all windows with and store hwnd in dict
    def window_enumeration_handler(hwnd, top_windows):
        top_windows[GetWindowText(hwnd).lower()] = hwnd
    EnumWindows(window_enumeration_handler, top_windows)
    
    # Detect elmocut
    elmocut_gui = top_windows['elmocut']
    
    # Bring window to front
    ShowWindow(elmocut_gui, 6) # Minimize
    ShowWindow(elmocut_gui, 9) # Un-minimize