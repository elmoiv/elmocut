from win32gui import EnumWindows, GetWindowText, ShowWindow
from os import path, makedirs, environ
from json import dump, load
from utils import terminal
import ctypes
import winreg

docs = path.join(environ['USERPROFILE'], 'Documents', 'elmocut')
json_path = path.join(docs, 'elmocut.json')

def is_admin():
    """
    Check if current user is Admin
    """
    return bool(ctypes.windll.shell32.IsUserAnAdmin())

def npcap_exists():
    """
    Check for Npcap driver
    """
    return path.exists(r'C:\Windows\SysWOW64\Npcap')

def duplicate_elmocut():
    """
    Check if there is more than 1 instance of elmoCut.exe
    """
    tasklist = terminal('tasklist')
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

def check_documents_dir():
    """
    Check if documents folder exists in order to store settings
    """
    makedirs(docs, exist_ok=True)
    if not path.exists(json_path):
        export_settings()

def import_settings():
    """
    Get stored settings
    """
    check_documents_dir()
    return load(open(json_path))

def export_settings(values=None):
    """
    Store current settings (or create new)
    """
    keys = ['dark', 'count', 'autostart', 'minimized', 'remember', 'killed']
    values = values if values else [True, 25, False, True, False, []]
    json = dict(zip(keys, values))
    dump(json, open(json_path, 'w'))

def update_settings(key, value):
    """
    Update certain setting item
    """
    s = import_settings()
    s[key] = value
    export_settings(list(s.values()))

def get_settings(key):
    """
    Get certain setting item by key
    """
    return import_settings()[key]

def add_to_startup(exe_path):
    """
    Add elmoCut to autostart
    """
    key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
            0,
            winreg.KEY_SET_VALUE
        )
    winreg.SetValueEx(key, 'elmocut', 0, winreg.REG_SZ, exe_path)

def remove_from_startup():
    """
    Remove elmoCut from autostart
    """
    key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
            0,
            winreg.KEY_WRITE
        )
    try:
        winreg.DeleteValue(key, 'elmocut')
    except FileNotFoundError:
        pass