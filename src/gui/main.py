from qdarkstyle import load_stylesheet
from pyperclip import copy

from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox, \
                            QMenu, QSystemTrayIcon, QAction
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWinExtras import QWinTaskbarButton

from ui.ui_main import Ui_MainWindow

from gui.settings import Settings
from gui.about import About
from gui.device import DeviceWindow

from networking.scanner import Scanner
from networking.killer import Killer

from tools.qtools import colored_item, MsgType, Buttons, clickable
from tools.utils_gui import set_settings, get_settings
from tools.utils import goto, is_connected

from assets import *

from bridge import ScanThread, UpdateThread

from constants import *

# from qt_material import build_stylesheet

class ElmoCut(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.icon = self.processIcon(app_icon)

        # Add window icon
        self.setWindowIcon(self.icon)
        self.setupUi(self)
        # stylesheet = build_stylesheet('dark_teal.xml', 0, {}, 'theme')
        # self.setStyleSheet(stylesheet)
        self.setStyleSheet(load_stylesheet())
        
        # Main Props
        self.scanner = Scanner()
        self.killer = Killer()

        # Settings props
        self.minimize = True
        self.remember = False
        self.autoupdate = True

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
        self.device_window = DeviceWindow(self, self.icon)

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
        self.settings_window.setWindowState(Qt.WindowNoState)

    def openAbout(self):
        """
        Open about window
        """
        self.about_window.hide()
        self.about_window.show()
        self.about_window.setWindowState(Qt.WindowNoState)

    def applySettings(self):
        """
        Apply saved settings
        """
        self.settings_window.updateElmocutSettings()

    def trayShowClicked(self):
        self.show()
        # Restore window state if was minimized before hidden
        self.setWindowState(Qt.WindowNoState)
        self.activateWindow()

    def tray_clicked(self, event):
        """
        Show elmoCut when tray icon is left-clicked
        """
        if event == QSystemTrayIcon.Trigger:
            self.trayShowClicked()

    def hide_all(self):
        """
        Hide option for tray (Hides window and settings)
        """
        self.hide()
        self.settings_window.hide()
        self.about_window.hide()

    def quit_all(self):
        """
        Unkill any killed device on exit from tray icon
        """
        self.killer.unkill_all()
        self.settings_window.close()
        self.about_window.close()
        self.tray_icon.hide()
        self.from_tray = True
        self.close()

    def showEvent(self, event):
        """
        https://stackoverflow.com/a/60123914/5305953
        Connect TaskBar icon to progressbar
        """
        self.taskbar_button = QWinTaskbarButton()
        self.taskbar_progress = self.taskbar_button.progress()
        self.taskbar_button.setWindow(self.windowHandle())
        self.pgbar.valueChanged.connect(self.taskbar_progress.setValue)

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
            event.accept()
            return
        
        # If event is recieved from close X button

        ## If minimize is true
        if self.minimize:
            event.ignore()
            self.hide_all()
            return

        ## If not, ukill all and shutdown
        self.killer.unkill_all()
        self.settings_window.close()
        self.about_window.close()

        self.hide()
        self.tray_icon.hide()

        QMessageBox.information(
            self,
            'Shutdown',
            'elmoCut will exit completely.\n\n'
            'Enable minimized from settings\n'
            'to be able to run in background.'
        )

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
        not_enabled = not self.current_index().admin
        
        self.btnKill.setEnabled(not_enabled)
        self.btnUnkill.setEnabled(not_enabled)
    
    def deviceDoubleClicked(self):
        """
        Open device info window (when not admin)
        """
        device = self.current_index()
        if device.admin:
            self.log('Admin device', color='orange')
            return
        
        self.device_window.load(device, self.tableScan.currentRow())
        self.device_window.hide()
        self.device_window.show()
        self.device_window.setWindowState(Qt.WindowNoState)
    
    def fillTableCell(self, row, column, text, colors=[]):
        # Center text in table cell
        ql = QTableWidgetItem()
        ql.setText(text)
        ql.setTextAlignment(Qt.AlignCenter)

        if colors:
            colored_item(ql, *colors)
        
        # Add cell to the specific location
        self.tableScan.setItem(row, column, ql)

    def fillTableRow(self, row, device: Device):
        colors = []
        if device.admin:
            colors = ['#00ff00', '#000000']
        else:
            colors = ['#ff0000', '#ffffff'] * (device.mac in self.killer.killed)
        
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

        # re-kill paused and update to current devices
        self.killer.rekill_stored(self.scanner.devices)
        
        # re-kill saved devices after exit
        for rem_device in self.scanner.devices:
            if rem_device.mac in get_settings('killed') * self.remember:
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
        self.taskbar_progress.setVisible(True)
        self.pgbar.setMaximum(self.scanner.device_count)
        self.taskbar_progress.setMaximum(self.scanner.device_count)
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
        self.taskbar_progress.setVisible(False)
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
