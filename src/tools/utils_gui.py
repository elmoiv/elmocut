from os import path, makedirs, environ
from json import dump, load, JSONDecodeError
import ctypes
import winreg

from tools.utils import terminal
from constants import *

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
    return path.exists(NPCAP_PATH)

def duplicate_elmocut():
    """
    Check if there is more than 1 instance of elmoCut.exe
    """
    tasklist = terminal('tasklist')
    return tasklist.lower().count('elmocut.exe') > 1

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
    keys = SETTINGS_KEYS
    values = values if values else SETTINGS_VALS
    json = dict(zip(keys, values))
    dump(json, open(json_path, 'w'))

def set_settings(key, value):
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

def repair_settings():
    """
    Rescue elmocut from new settings not found after updates
    """
    original = dict(zip(SETTINGS_KEYS, SETTINGS_VALS))
    
    try:
        s = import_settings()
        for key in s:
            original[key] = s[key]
    except JSONDecodeError:
        pass
        
    export_settings(list(original.values()))

def add_to_startup(exe_path):
    """
    Add elmoCut to autostart
    """
    key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            HKEY_AUTOSTART_PATH,
            0,
            winreg.KEY_SET_VALUE
        )
    winreg.SetValueEx(
        key,
        'elmocut',
        0,
        winreg.REG_SZ, exe_path
    )

def remove_from_startup():
    """
    Remove elmoCut from autostart
    """
    key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            HKEY_AUTOSTART_PATH,
            0,
            winreg.KEY_WRITE
        )
    try:
        winreg.DeleteValue(key, 'elmocut')
    except FileNotFoundError:
        pass