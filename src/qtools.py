from win32gui import EnumWindows, GetWindowText, ShowWindow
from PyQt5.QtWidgets import QMessageBox
from os import popen, path

def msg_box(title, text, icon=None, buttons=QMessageBox.Ok):
    """
    Main app independent QMessageBox
    """
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(text)
    if icon:
        msg.setWindowIcon(icon)
    msg.setStandardButtons(buttons)
    return msg.exec_()

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
