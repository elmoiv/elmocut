from os import path, makedirs, rename
from json import dump, load, JSONDecodeError
import ctypes
import winreg
import sys
import threading
import subprocess
from tools.utils import terminal
from constants import *
import os
from os import replace as os_replace

_settings_lock = threading.Lock()

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
    makedirs(DOCUMENTS_PATH, exist_ok=True)
    if not path.exists(SETTINGS_PATH):
        export_settings()

def _import_settings_unlocked():
    """
    Internal: read settings WITHOUT acquiring the lock.
    Only call this from inside a block that already holds _settings_lock.
    """
    check_documents_dir()
    return load(open(SETTINGS_PATH))

def _export_settings_unlocked(values=None):
    """
    Internal: write settings WITHOUT acquiring the lock, atomically.
    Only call this from inside a block that already holds _settings_lock.
    """
    keys = SETTINGS_KEYS
    values = values if values else SETTINGS_VALS
    json = dict(zip(keys, values))

    tmp_path = SETTINGS_PATH + '.tmp'
    with open(tmp_path, 'w') as f:
        dump(json, f)
    os_replace(tmp_path, SETTINGS_PATH)  # atomic on Windows (same volume)

def import_settings():
    """
    Get stored settings
    """
    with _settings_lock:
        return _import_settings_unlocked()

def export_settings(values=None):
    """
    Store current settings (or create new)
    """
    with _settings_lock:
        _export_settings_unlocked(values)

def set_settings(key, value):
    """
    Update certain setting item (single atomic read-modify-write)
    """
    with _settings_lock:
        s = _import_settings_unlocked()
        s[key] = value
        _export_settings_unlocked(list(s.values()))

def get_settings(key):
    """
    Get certain setting item by key
    """
    with _settings_lock:
        return _import_settings_unlocked()[key]

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

def migrate_settings_file():
    old_exists = path.exists(OLD_SETTINGS_PATH)
    new_exists = path.exists(SETTINGS_PATH)
    if old_exists and not new_exists:
        try:
            makedirs(DOCUMENTS_PATH, exist_ok=True)
            rename(OLD_SETTINGS_PATH, SETTINGS_PATH)
        except Exception as e:
            print(f'Migrating settings error: {e}')
            print('New settings file created instead.')

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

def restart_gui_app(_app):
    """
    Relaunch the current executable as a new process, then forcibly
    terminate this one. Passes --restarting so the new instance
    tolerates a brief overlap with the old one during shutdown.
    """
    executable = sys.executable

    args = [a for a in sys.argv if a != executable]
    args = [executable] + args + ['--restarting']

    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200

    subprocess.Popen(
        args,
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        close_fds=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    _app.from_tray = True   # bypass minimize-to-tray on close
    _app.close()

    os._exit(0)