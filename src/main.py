from qdarkstyle import load_stylesheet
from pyperclip import copy

from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox, \
                            QMenu, QSystemTrayIcon, QAction
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

from ui_main import Ui_MainWindow
from settings import Settings
from about import About

from qtools import colored_item, MsgType, Buttons

from scanner import Scanner
from killer import Killer

from assets import app_icon, \
                   kill_icon, killall_icon, \
                   unkill_icon, unkillall_icon, \
                   scan_easy_icon, scan_hard_icon, \
                   settings_icon, about_icon

from utils_gui import set_settings, get_settings
from utils import goto, check_connection, is_connected

from bridge import ScanThread, UpdateThread

class ElmoCut(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.version = '1.0.4'
        self.icon = self.processIcon(app_icon)

        # Add window icon
        self.setWindowIcon(self.icon)
        self.setupUi(self)
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
        
        # We send elmocut to the settings window
        self.settings_window = Settings(self, self.icon)
        self.about_window = About(self, self.icon)

        self.applySettings()

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

        self.pgbar.setVisible(False)

        # Table Widget
        self.tableScan.itemClicked.connect(self.deviceClicked)
        self.tableScan.cellClicked.connect(self.cellClicked)
        self.tableScan.setColumnCount(4)
        self.tableScan.verticalHeader().setVisible(False)
        self.tableScan.setHorizontalHeaderLabels(['IP Address', 'MAC Address', 'Vendor', 'Type'])

        '''
           System tray icon and it's tray menu
        '''
        show_option = QAction('Show', self)
        hide_option = QAction('Hide', self)
        quit_option = QAction('Quit', self)
        kill_option = QAction(self.processIcon(kill_icon), '&Kill All', self)
        unkill_option = QAction(self.processIcon(unkill_icon),'&Unkill All', self)
        
        show_option.triggered.connect(self.show)
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
    
    def connected(self):
        """
        Prompt when disconnected
        """
        if is_connected():
            return True
        self.log('Connection lost!', 'red')
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
        self.settings_window.currentSettings()
        self.settings_window.show()

    def openAbout(self):
        """
        Open about window
        """
        self.about_window.hide()
        self.about_window.show()

    def applySettings(self):
        """
        Apply saved settings
        """
        self.settings_window.updateElmocutSettings()

    def tray_clicked(self, event):
        """
        Show elmoCut when tray icon is left-clicked
        """
        if event == QSystemTrayIcon.Trigger:
            self.show()

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

    def resizeEvent(self, event=True):
        """
        Auto resize table widget columns dynamically
        """
        for i in range(4):
            self.tableScan.setColumnWidth(i, self.tableScan.width() // 4)

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
        cell = list(device.values())[column]
        self.lblcenter.setText(cell)
        copy(cell)

    def deviceClicked(self):
        """
        Disable kill, unkill buttons when admins are selected
        """
        not_enabled = not self.current_index()['admin']
        
        self.btnKill.setEnabled(not_enabled)
        self.btnUnkill.setEnabled(not_enabled)
    
    def showDevices(self):
        """
        View scanlist devices with correct colors processed
        """
        self.tableScan.clearSelection()
        self.tableScan.clearContents()
        self.tableScan.setRowCount(len(self.scanner.devices))

        for row, device in enumerate(self.scanner.devices):
            for column, item in enumerate(device.values()):
                # Skip 'admin' key
                if type(item) == bool:
                    continue
                
                # Center text in eah cell
                ql = QTableWidgetItem()
                ql.setText(item)
                ql.setTextAlignment(Qt.AlignCenter)
                
                # Highlight Admins and killed devices
                if device['admin']:
                    colored_item(ql, '#00ff00', '#000000')
                if device['mac'] in self.killer.killed:
                    colored_item(ql, '#ff0000', '#ffffff')
                
                # Add cell to the row
                self.tableScan.setItem(row, column, ql)
        
        status = f'{len(self.scanner.devices) - 2} devices' \
                 f' ({len(self.killer.killed)} killed)'
        
        self.lblright.setText(status)
        self.tray_icon.setToolTip(status)

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
            if rem_device['mac'] in get_settings('killed') * self.remember:
                self.killer.kill(rem_device)

        # clear old database
        self.killer.release()

        self.log(
            f'Found {len(self.scanner.devices) - 1} devices.',
            'orange'
        )

        self.showDevices()

    @check_connection
    def kill(self):
        """
        Apply ARP spoofing to selected device
        """
        if not self.tableScan.selectedItems():
            self.log('No device selected.', 'red')
            return

        device = self.current_index()
        
        if device['mac'] in self.killer.killed:
            self.log('Device is already killed.', 'red')
            return
        
        # Killing process
        self.killer.kill(device)
        set_settings('killed', list(self.killer.killed) * self.remember)
        self.log('Killed ' + device['ip'], 'fuchsia')
        
        self.showDevices()
    
    @check_connection
    def unkill(self):
        """
        Disable ARP spoofing on previously spoofed devices
        """
        if not self.tableScan.selectedItems():
            self.log('No device selected.', 'red')
            return

        device = self.current_index()
            
        if device['mac'] not in self.killer.killed:
            self.log('Device is already unkilled.', 'red')
            return
        
        # Unkilling process
        self.killer.unkill(device)
        set_settings('killed', list(self.killer.killed) * self.remember)
        self.log('Unkilled ' + device['ip'], 'lime')

        self.showDevices()
    
    @check_connection
    def killAll(self):
        """
        Kill all scanned devices except admins
        """
        self.killer.kill_all(self.scanner.devices)
        set_settings('killed', list(self.killer.killed) * self.remember)
        self.log('Killed All devices.', 'fuchsia')

        self.showDevices()

    @check_connection
    def unkillAll(self):
        """
        Unkill all killed devices except admins
        """
        self.killer.unkill_all()
        set_settings('killed', list(self.killer.killed) * self.remember)
        self.log('Unkilled All devices.', 'lime')

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
        if not self.connected():
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
        __import__('gc').collect()
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
        
        if new_version != self.version:
            if MsgType.INFO(
                self,
                'elmoCut Update Available',
                'A new version is available.\n'
                f'Do you want to download {new_version}?',
                Buttons.YES | Buttons.NO
            ) == Buttons.YES:
                goto(update_url)
        
        if new_version == self.version and self.update_thread.prompt_if_latest:
            MsgType.INFO(
                self.settings_window, # Run this within settings window
                'Check for update',
                'You have the latest version installed.'
            )
