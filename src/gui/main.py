from qdarkstyle import load_stylesheet
from pyperclip import copy

from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox, \
                            QMenu, QSystemTrayIcon
from PyQt6.QtGui import QPixmap, QIcon, QAction
from PyQt6.QtCore import Qt
from ui.ui_main import Ui_MainWindow

from gui.settings import Settings
from gui.about import About
from gui.device import DeviceWindow

from networking.scanner import Scanner
from networking.killer import Killer
from networking.diverter import ElmoDivert

from tools.qtools import colored_item, MsgType, Buttons, clickable
from tools.utils_gui import set_settings, get_settings, restart_gui_app
from tools.utils import goto, is_connected

from assets import *

from bridge import ScanThread, UpdateThread

from constants import *
import os
import signal
import sys

# from qt_material import build_stylesheet

def force_close():
    try:
        os.kill(os.getpid(), signal.SIGTERM)
    except:
        sys.exit(0)

class ElmoCut(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.icon = self.processIcon(app_icon)

        # Add window icon
        self.setWindowIcon(self.icon)
        self.setupUi(self)
        self.setStyleSheet(load_stylesheet())
        
        # Main Props
        self.watched_devices: dict[str, ElmoDivert] = {}
        self.scanner = Scanner(self)
        self.killer = Killer()

        # Settings props
        self.minimize = True
        self.remember = False
        self.autoupdate = True
        self.ip_forwarding_enabled = False

        self.from_tray = False

        # Threading
        self.scan_thread = ScanThread()
        self.scan_thread.thread_finished.connect(self.ScanThread_Reciever)
        self.scan_thread.progress.connect(self.pgbar.setValue)

        self.update_thread = UpdateThread()
        self.update_thread.thread_finished.connect(self.UpdateThread_Reciever)
        
        # Initialize other sub-windows
        self.settings_window = Settings(self, self.icon)
        self.about_window = About(self, self.icon)
        self.device_windows: dict[str, DeviceWindow] = {}

        # Connect buttons
        self.buttons = [
            (self.btnScanEasy,   self.scanEasy,      scan_easy_icon,  'Arping Scan'),
            (self.btnScanHard,   self.scanHard,      scan_hard_icon,  'Pinging Scan'),
            (self.btnKill,       self.kill,          kill_icon,       'Kill selected device'),
            (self.btnUnkill,     self.unkill,        unkill_icon,     'Un-kill selected device'),
            (self.btnKillAll,    self.killAll,       killall_icon,    'Kill all devices'),
            (self.btnUnkillAll,  self.unkillAll,     unkillall_icon,  'Un-kill all devices'),
            (self.btnSettings,   self.openSettings,  settings_icon,   'View elmoCut settings'),
            (self.btnAbout,      self.openAbout,     about_icon,      'About elmoCut')
        ] 
        
        for btn, btn_func, btn_icon, btn_tip in self.buttons:
            btn.setToolTip(btn_tip)
            btn.clicked.connect(btn_func)
            btn.setIcon(self.processIcon(btn_icon))

        clickable(self.lblDonate).connect(self.buymeacoffee)
        self.setImage(self.lblDonate, donate_icon)
        
        self.pgbar.setVisible(False)

        # Table Widget
        self.tableScan.itemClicked.connect(self.deviceClicked)
        self.tableScan.itemDoubleClicked.connect(self.deviceDoubleClicked)
        self.tableScan.cellClicked.connect(self.cellClicked)
        self.tableScan.setColumnCount(len(TABLE_HEADER_LABELS))
        self.tableScan.verticalHeader().setVisible(False)
        self.tableScan.setHorizontalHeaderLabels(TABLE_HEADER_LABELS)
        self.tableScan.setShowGrid(False)
        # self.tableScan.setStyleSheet("QTableWidget::item { border: none; }")

        '''
           System tray icon and it's tray menu
        '''
        show_option = QAction('Show', self)
        hide_option = QAction('Hide', self)
        quit_option = QAction('Quit', self)
        kill_option = QAction(self.processIcon(kill_icon), '&Kill All', self)
        unkill_option = QAction(self.processIcon(unkill_icon),'&Unkill All', self)
        
        show_option.triggered.connect(self.trayShowClicked)
        hide_option.triggered.connect(self.hide_all)
        quit_option.triggered.connect(self.quit_all)
        kill_option.triggered.connect(self.killAll)
        unkill_option.triggered.connect(self.unkillAll)
        
        tray_menu = QMenu()
        tray_menu.addAction(show_option)
        tray_menu.addAction(hide_option)
        tray_menu.addSeparator()
        tray_menu.addAction(kill_option)
        tray_menu.addAction(unkill_option)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_option)
        
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.icon)
        self.tray_icon.setToolTip('elmoCut')
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_clicked)

        self.applySettings()
    
    @staticmethod
    def processIcon(icon_data):
        """
        Create icon pixmap object from raw data
        """
        pix = QPixmap()
        icon = QIcon()
        pix.loadFromData(icon_data)
        icon.addPixmap(pix)
        return icon
    
    def setImage(self, widget, raw_image):
        pix = QPixmap()
        pix.loadFromData(raw_image)
        widget.setPixmap(pix)
    
    def connected(self, show_msg_box=False):
        """
        Prompt when disconnected
        """
        if is_connected(current_iface=self.scanner.iface):
            return True
        self.log('Connection lost!', 'red')
        if show_msg_box:
            QMessageBox.critical(self, 'elmoCut', 'Connection Lost!')
        return False

    def log(self, text, color='white'):
        """
        Print log info at left label
        """
        self.lblleft.setText(f"<font color='{color}'>{text}</font>")
    
    def openSettings(self):
        """
        Open settings window
        """
        self.settings_window.hide()
        self.settings_window.loadInterfaces()
        self.settings_window.currentSettings()
        self.settings_window.show()
        self.settings_window.setWindowState(Qt.WindowState.WindowNoState)

    def openAbout(self):
        """
        Open about window
        """
        self.about_window.hide()
        self.about_window.show()
        self.about_window.setWindowState(Qt.WindowState.WindowNoState)

    def applySettings(self):
        """
        Apply saved settings
        """
        self.settings_window.updateElmocutSettings()

    def trayShowClicked(self):
        self.show()
        # Restore window state if was minimized before hidden
        self.setWindowState(Qt.WindowState.WindowNoState)
        self.activateWindow()

    def tray_clicked(self, event):
        """
        Show elmoCut when tray icon is left-clicked
        """
        if event == QSystemTrayIcon.ActivationReason.Trigger:
            self.trayShowClicked()

    def sync_ip_forwarding_state(self):
        """
        Detect if IP forwarding was changed manually outside elmoCut
        (e.g. via netsh or the registry directly) and reconcile our
        stored setting + UI checkbox + in-memory flag to match reality.
        """
        from networking.diverter import ElmoDivert
        actual = ElmoDivert.is_ip_forwarding_enabled(self.scanner.iface.name)
        stored = get_settings('ip_forwarding')

        self.ip_forwarding_enabled = actual

        if actual != stored:
            set_settings('ip_forwarding', actual)
            self.settings_window.chkIpForwarding.setChecked(actual)

            self.log(
                f"IP forwarding was {'enabled' if actual else 'disabled'} "
                "outside elmoCut — settings updated to match.",
                'yellow'
            )

    def hide_all(self):
        """
        Hide option for tray (Hides window and settings)
        """
        self.hide()
        self.settings_window.hide()
        self.about_window.hide()

    def quit_all(self):
        self.stop_all_watching() 
        self.killer.unkill_all()
        self.settings_window.close()
        self.about_window.close()
        for window in list(self.device_windows.values()):
            window.close()
        self.tray_icon.hide()
        self.from_tray = True
        self.close()

    def stop_all_watching(self):
        """
        Stop every active URL-watching session.
        Only ever called when elmoCut itself is closing.
        """
        for mac, divert in list(self.watched_devices.items()):
            divert.stop()
        self.watched_devices.clear()

    def request_enable_ip_forwarding(self):
        """
        Prompt to enable IP forwarding when watching is attempted while it's off.
        """
        if MsgType.WARN(
            self,
            'IP Forwarding Required',
            'IP forwarding is currently disabled.\n'
            'You need to enable it first to watch device traffic.\n\n'
            'Enabling it will make killing devices not effective, '
            'and all currently killed devices will be unkilled.\n\n'
            'Enable IP forwarding now?',
            Buttons.YES | Buttons.NO
        ) == Buttons.NO:
            return False

        ElmoDivert.enable_ip_forwarding(self.scanner.iface.name)
        set_settings('ip_forwarding', True)
        self.ip_forwarding_enabled = True
        self.killer.unkill_all()
        set_settings('killed', [])

        return True

    def request_disable_ip_forwarding(self):
        """
        Prompt to disable IP forwarding when killing is attempted while it's on.
        """
        if MsgType.WARN(
            self,
            'Disable IP Forwarding Required',
            'IP forwarding is currently enabled.\n'
            'To kill devices you must disable it first.\n\n'
            'Disabling it will make URL watching not effective, '
            'and all currently watched devices will be unwatched.\n\n'
            'Disable IP forwarding now?',
            Buttons.YES | Buttons.NO
        ) == Buttons.NO:
            return False

        ElmoDivert.disable_ip_forwarding(self.scanner.iface.name)
        set_settings('ip_forwarding', False)
        self.ip_forwarding_enabled = False
        self.stop_all_watching()

        return True

    def resizeEvent(self, event=True):
        """
        Auto resize table widget columns dynamically
        """
        label_count = len(TABLE_HEADER_LABELS)
        for i in range(label_count):
            self.tableScan.setColumnWidth(i, self.tableScan.width() // label_count)

    def closeEvent(self, event):
        """
        Run in background if self.minimize is True else exit
        """
        # If event recieved from tray icon
        if self.from_tray:
            force_close()
            event.accept()
            return
        
        # If event is recieved from close X button

        ## If minimize is true
        if self.minimize:
            event.ignore()
            self.hide_all()
            return

        ## If not, ukill all and shutdown
        self.stop_all_watching()
        self.killer.unkill_all()
        self.settings_window.close()
        self.about_window.close()

        for window in list(self.device_windows.values()):
            window.close()

        self.hide()
        self.tray_icon.hide()

        QMessageBox.information(
            self,
            'Shutdown',
            'elmoCut will exit completely.\n\n'
            'Enable minimized from settings\n'
            'to be able to run in background.'
        )

        force_close()

        event.accept()

    def current_index(self):
        return self.scanner.devices[self.tableScan.currentRow()]
    
    def cellClicked(self, row, column):
        """
        Copy selected cell data to clipboard
        """
        # Get current row
        device = self.current_index()

        # Get cell text using dict.values instead of .itemAt()
        cell = list(device.to_dict().values())[column]
        
        if len(cell) > 20:
            cell = cell[:20] + '...'
        
        self.lblcenter.setText(cell)
        copy(cell)

    def deviceClicked(self):
        """
        Disable kill, unkill buttons when admins are selected
        """
        device: Device = self.current_index()
        is_admin = device.admin
        is_watched = device.mac in self.watched_devices
        self.btnKill.setEnabled(not (is_admin or is_watched))
        self.btnUnkill.setEnabled(not (is_admin or is_watched))
    
    def deviceDoubleClicked(self):
        """
        Open an independent window per device.
        Each device gets its own DeviceWindow instance so multiple
        devices can be watched simultaneously without interfering.
        """
        device: Device = self.current_index()
        if device.admin:
            self.log('Admin device', color='orange')
            return

        if device.mac in self.watched_devices and self.watched_devices[device.mac].is_running():
            self.log(f"{device.ip} is already being watched", 'yellow')

        # Reuse the window if this exact device already has one open,
        # otherwise spin up a brand-new independent window
        window = self.device_windows.get(device.mac)
        if window is None:
            window = DeviceWindow(self, self.icon)
            self.device_windows[device.mac] = window

        window.load(device, self.tableScan.currentRow())
        window.show()
        window.setWindowState(Qt.WindowState.WindowNoState)
        window.activateWindow()
        window.raise_()
    
    def fillTableCell(self, row, column, text, colors=[]):
        # Center text in table cell
        ql = QTableWidgetItem()
        ql.setText(text)
        ql.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        if colors:
            colored_item(ql, *colors)
        
        # Add cell to the specific location
        self.tableScan.setItem(row, column, ql)

    def fillTableRow(self, row, device: Device):
        if device.admin:
            colors = ['#00ff00', '#000000']
        elif device.mac in self.watched_devices:
            colors = ['#ffff00', '#000000']
        elif device.mac in self.killer.killed:
            colors = ['#ff0000', '#ffffff']
        else:
            colors = []
        
        props = device.to_dict()
        del props['admin']

        for column, prop in enumerate(props.values()):
            self.fillTableCell(row, column, prop, colors)

    def showDevices(self):
        """
        View scanlist devices with correct colors processed
        """
        self.tableScan.clearSelection()
        self.tableScan.clearContents()
        self.tableScan.setRowCount(len(self.scanner.devices))

        for row, device in enumerate(self.scanner.devices):
            print(f'>> {device}')
            self.fillTableRow(row, device)
        
        status = f'{len(self.scanner.devices) - 2} devices' \
                 f' ({len(self.killer.killed)} killed)'
        
        status_tray = f'Devices Found: {len(self.scanner.devices) - 2}\n' \
                      f'Devices Killed: {len(self.killer.killed)}\n' \
                      f'Interface: {self.scanner.iface.name}'
        
        self.lblright.setText(status)
        self.tray_icon.setToolTip(status_tray)

        # Show selected cell data
        self.lblcenter.setText('Nothing Selected')
    
    def processDevices(self):
        """
        Rekill any paused device after scan
        """
        self.tableScan.clearSelection()

        # first device in list is the router
        self.killer.router = self.scanner.router

        watched_macs = set(self.watched_devices.keys())

        # re-kill paused and update to current devices
        self.killer.rekill_stored(self.scanner.devices, exclude_macs=watched_macs)
        
        # re-kill saved devices after exit
        for rem_device in self.scanner.devices:
            if rem_device.mac in get_settings('killed') * self.remember and rem_device.mac not in watched_macs:
                self.killer.kill(rem_device)

        # clear old database
        self.killer.release()

        self.log(
            f'Found {len(self.scanner.devices) - 2} devices.',
            'orange'
        )

        self.showDevices()

    # @check_connection
    def kill(self):
        """
        Apply ARP spoofing to selected device
        """
        if not self.connected():
            return
        
        if not self.tableScan.selectedItems():
            self.log('No device selected', 'red')
            return

        device = self.current_index()

        if device.mac in self.watched_devices:
            MsgType.WARN(
                self,
                'Cannot Kill Device!',
                'This device is currently being watched.\nStop watching it first to kill it.'
            )
            return

        if self.ip_forwarding_enabled:
            if not self.request_disable_ip_forwarding():
                return
            self.showDevices()
        
        if device.mac in self.killer.killed:
            self.log('Device is already killed', 'red')
            return
        
        # Killing process
        self.killer.kill(device)
        set_settings('killed', list(self.killer.killed) * self.remember)
        self.log('Killed ' + device.ip, 'fuchsia')
        
        self.showDevices()
    
    # @check_connection
    def unkill(self):
        """
        Disable ARP spoofing on previously spoofed devices
        """
        if not self.connected():
            return
        
        if not self.tableScan.selectedItems():
            self.log('No device selected', 'red')
            return

        device = self.current_index()
            
        if device.mac not in self.killer.killed:
            self.log('Device is already unkilled', 'red')
            return
        
        # Unkilling process
        self.killer.unkill(device)
        set_settings('killed', list(self.killer.killed) * self.remember)
        self.log('Unkilled ' + device.ip, 'lime')

        self.showDevices()
    
    # @check_connection
    def killAll(self):
        """
        Kill all scanned devices except admins
        """
        if not self.connected():
            return

        if self.ip_forwarding_enabled:
            if not self.request_disable_ip_forwarding():
                return
            self.showDevices()

        self.killer.kill_all(self.scanner.devices)
        set_settings('killed', list(self.killer.killed) * self.remember)
        self.log('Killed All devices', 'fuchsia')

        self.showDevices()

    # @check_connection
    def unkillAll(self):
        """
        Unkill all killed devices except admins
        """
        if not self.connected():
            return
        
        self.killer.unkill_all()
        set_settings('killed', list(self.killer.killed) * self.remember)
        self.log('Unkilled All devices', 'lime')

        self.showDevices()

    def scanEasy(self):
        """
        Easy Scan button connector
        """
        self.ScanThread_Starter()
    
    def scanHard(self):
        """
        Hard Scan button connector
        """
        # Set correct max for progress bar
        self.ScanThread_Starter(scan_type=1)

    def ScanThread_Starter(self, scan_type=0):
        """
        Scan Thread Starter
        """
        if not self.connected(show_msg_box=True):
            return

        self.centralwidget.setEnabled(False)

        # Save copy of killed devices
        self.killer.store()

        self.killer.unkill_all()

        self.log(
            ['Arping', 'Pinging'][scan_type] + ' your network...',
            ['aqua', 'fuchsia'][scan_type]
        )

        self.pgbar.setVisible(True)
        self.pgbar.setMaximum(self.scanner.device_count)
        self.pgbar.setValue(self.scanner.device_count * (not scan_type))
        
        self.scan_thread.scanner = self.scanner
        self.scan_thread.scan_type = scan_type
        self.scan_thread.start()

    def ScanThread_Reciever(self):
        """
        Scan Thread results reciever
        """
        self.centralwidget.setEnabled(True)
        self.pgbar.setVisible(False)
        self.processDevices()
    
    def UpdateThread_Starter(self):
        """
        Update Thread starter
        """
        if self.autoupdate:
            self.update_thread.prompt_if_latest = False
            self.update_thread.start()

    def UpdateThread_Reciever(self):
        """
        Update Thread reciever
        """
        new_version = self.update_thread.github_version
        update_url = self.update_thread.url
        
        if new_version == 'None':
            return
        
        if new_version != VERSION:
            if MsgType.INFO(
                self,
                'elmoCut Update Available',
                'A new version is available.\n'
                f'Do you want to download {new_version}?',
                Buttons.YES | Buttons.NO
            ) == Buttons.YES:
                goto(update_url)
        
        if new_version == VERSION and self.update_thread.prompt_if_latest:
            MsgType.INFO(
                self.settings_window, # Run this within settings window
                'Check for update',
                'You have the latest version installed.'
            )
    
    # Open BuyMeACoffee page
    buymeacoffee = lambda self: goto('https://www.buymeacoffee.com/elmoiv')
