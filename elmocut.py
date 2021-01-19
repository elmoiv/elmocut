import sys
from os import system as webbrowser

from qdarkstyle import load_stylesheet
from pyperclip import copy

from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtGui import QColor, QPixmap, QIcon

from utils import is_connected
from scanner import Scanner
from killer import Killer

from assets import app_icon, \
                        kill_icon, killall_icon, \
                        unkill_icon, unkillall_icon, \
                        scan_easy_icon, scan_hard_icon, \
                        settings_icon
from tools import msg_box, duplicate_elmocut, \
                        bring_elmocut_tofront, npcap_exists
from connector import ScanThread
from ui import Ui_MainWindow

CONNECTED = True

def check_connection(func):
    '''
    Connection checker decorator
    '''
    def wrapper(*args, **kargs):
        # for def func(self): in class
        # will return kargs = {}
        # and return args = (<__main__.ElmoCut object at 0x00000....etc>, False)
        # so we chose the "self" reference: args[0] = <__main__.ElmoCut object at 0x00000....etc>
        if CONNECTED:
            return func(args[0])
    return wrapper

class ElmoCut(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.version = 0.1

        # Add window icon
        self.setWindowIcon(self.processIcon(app_icon))

        self.setupUi(self)
        self.setStyleSheet(load_stylesheet())
        
        # Main Props
        self.scanner = None
        self.killer = None

        # Threading
        self.scan_thread = ScanThread()
        # Main signal reciever for scan_thread.run()
        self.scan_thread.thread_finished_signal.connect(self.ScanThread_Reciever)
        # Progress bar singal reciever for self.scanner.pinging_watcher()
        self.scan_thread.progress.connect(self.pgbar.setValue)
        
        # Connect buttons
        self.buttons = [
            (self.btnScanEasy,  self.scanEasy,     scan_easy_icon, 'Arping Scan'),
            (self.btnScanHard,  self.scanHard,     scan_hard_icon, 'Pinging Scan'),
            (self.btnKill,      self.kill,         kill_icon,      'Kill selected device'),
            (self.btnUnkill,    self.unkill,       unkill_icon,    'Un-kill selected device'),
            (self.btnKillAll,   self.killAll,      killall_icon,   'Kill all devices'),
            (self.btnUnkillAll, self.unkillAll,    unkillall_icon, 'Un-kill all devices'),
            (self.btnSettings,  self.showSettings, settings_icon,  'View elmoCut settings')
            ]
        
        for btn, btn_func, btn_icon, btn_tip in self.buttons:
            btn.clicked.connect(btn_func)
            btn.setIcon(
                self.processIcon(btn_icon)
            )
            btn.setToolTip(btn_tip)

        self.pgbar.setVisible(False)

        # Table Widget
        self.tableScan.itemClicked.connect(self.deviceClicked)
        self.tableScan.cellClicked.connect(self.cellClicked)
        self.tableScan.setColumnCount(4)
        self.tableScan.verticalHeader().setVisible(False)
        self.tableScan.setHorizontalHeaderLabels(['IP Address','MAC Address','Vendor','Type'])

    @staticmethod
    def processIcon(icon_data):
        '''
        Create icon pixmap object from raw data
        '''
        pix = QPixmap()
        icon = QIcon()
        
        pix.loadFromData(icon_data)
        icon.addPixmap(pix)
        
        return icon

    def run(self):
        QApplication.processEvents()

    def resizeEvent(self, event=True):
        '''
        Auto resize table widget columns dynamically
        '''
        for i in range(4):
            self.tableScan.setColumnWidth(i, self.tableScan.width() // 4)

    def closeEvent(self, event):
        '''
        Unkill any killed device on exit event
        '''
        self.killer.unkill_all()
    
    def coloredItem(self, elmnt, colors):
        '''
        Add colors to Table rows
        '''
        elmnt.setBackground(QColor(colors[0]))
        elmnt.setForeground(QColor(colors[1]))
    
    def log(self, text, color='white'):
        '''
        Print log info at left label
        '''
        self.lblleft.setText(f"<font color='{color}'>{text}</font>")
    
    def connected(self):
        '''
        Check for Internet connection
        '''
        globals()['CONNECTED'] = True

        if not is_connected():
            self.log('No Internet Connection', 'red')
            self.pgbar.setVisible(False)

            globals()['CONNECTED'] = False
        
        return CONNECTED

    def current_index(self):
        return self.scanner.devices[self.tableScan.currentRow()]
    
    def reListDevices(self):
        '''
        View scanlist devices with correct colors processed
        '''
        self.tableScan.clearSelection()
        
        # Clearing QTableWidget
        # https://stackoverflow.com/a/31564541/5305953
        self.tableScan.clearContents()

        self.tableScan.setRowCount(len(self.scanner.devices))

        print('Started listing...')
        for row, device in enumerate(self.scanner.devices):
            for column, item in enumerate(device.values()):
                
                # Center text in eah cell
                ql = QTableWidgetItem()
                ql.setText(item)
                ql.setTextAlignment(Qt.AlignCenter)
                
                # Highlight Admins and killed devices
                if device['type'] in ['Router', 'Me']:
                    self.coloredItem(ql, ['#00ff00', '#000000'])
                if device['mac'] in self.killer.killed:
                    self.coloredItem(ql, ['#ff0000', '#ffffff'])
                
                # Add cell to the row
                self.tableScan.setItem(row, column, ql)
        
        self.lblright.setText(
                            f'{len(self.scanner.devices) - 1} devices'
                            f' ({len(self.killer.killed)} killed)'
        )
        
        # Show selected cell data
        self.lblcenter.setText('Nothing Selected')
    
    def cellClicked(self, row, column):
        '''
        Copy selected cell data to clipboard
        '''
        # Get current row
        device = self.current_index()

        # Get cell text using dict.values instead of .itemAt()
        cell = list(device.values())[column]
        copy(cell)
        self.lblcenter.setText(cell)

    def deviceClicked(self):
        '''
        Disable kill, unkill buttons when admins are selected
        '''
        device = self.current_index()
        
        is_admin = device['type'] not in 'RouterMe'
        
        self.btnKill.setEnabled(is_admin)
        self.btnUnkill.setEnabled(is_admin)

    @check_connection
    def kill(self):
        '''
        Apply ARP spoofing to selected device
        '''
        if not self.tableScan.selectedItems():
            self.log('No device selected.', 'aqua')
            return

        device = self.current_index()
        
        if device['mac'] in self.killer.killed:
            self.log('Device is already killed.', 'red')
            return
        
        # Killing process
        self.killer.kill(device)
        self.log('Killed ' + device['ip'], 'fuchsia')
        
        self.reListDevices()
    
    @check_connection
    def unkill(self):
        '''
        Disable ARP spoofing on previously spoofed devices
        '''
        if not self.tableScan.selectedItems():
            self.log('No device selected.', 'aqua')
            return

        device = self.current_index()
            
        if device['mac'] not in self.killer.killed:
            self.log('Device is already unkilled.', 'red')
            return
        
        # Unkilling process
        self.killer.unkill(device)
        self.log('Unkilled ' + device['ip'], 'lime')

        self.reListDevices()
    
    @check_connection
    def killAll(self):
        '''
        Kill all scanned devices except admins
        '''
        self.killer.kill_all(self.scanner.devices)
        self.reListDevices()
        self.log('Killed All devices.')
    
    @check_connection
    def unkillAll(self):
        '''
        Unkill all killed devices except admins
        '''
        self.killer.unkill_all()
        self.reListDevices()
        
        self.log('Unkilled All devices.')

    def process_devices(self):
        '''
        Perform scan on devices connected to same access point
        '''
        self.tableScan.clearSelection()
        
        # first device in list is the router
        self.killer.router = self.scanner.router

        # re-kill paused and update to current devices
        self.killer.rekill_stored(self.scanner.devices)

        # clear old database
        self.killer.release()

        # Processing items for the table view
        self.reListDevices()

        self.log(
            f'Found {len(self.scanner.devices) - 1} devices.',
            'yellow'
        )
    
    def scanEasy(self):
        '''
        Easy Scan button connector
        '''
        self.ScanThread_Starter()
    
    def scanHard(self):
        '''
        Hard Scan button connector
        '''
        # Set correct max for progress bar
        self.pgbar.setMaximum(self.scanner.device_count)
        self.pgbar.setValue(0)
        self.pgbar.setVisible(True)

        self.ScanThread_Starter(scan_type=1)
    
    def ScanThread_Starter(self, scan_type=0):
        '''
        self.scan_thread QThread Starter
        '''
        if not self.connected():
            return
        
        self.centralwidget.setEnabled(False)
        self.run()
        
        # Save copy of killed devices
        self.killer.store()
        
        self.killer.unkill_all()
        
        self.log(
            ['Arping', 'Pinging'][scan_type] + ' your network...',
            ['aqua', 'fuchsia'][scan_type]
        )
        
        self.scan_thread.scanner = self.scanner
        self.scan_thread.scan_type = scan_type
        self.scan_thread.start()

    def ScanThread_Reciever(self, process_devices_func):
        '''
        self.scan_thread QThread results reciever
        '''
        self.centralwidget.setEnabled(True)
        self.process_devices()
        self.pgbar.setVisible(False)

    def showSettings(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon = ElmoCut.processIcon(app_icon)
    
    # Check if Npcap is installed
    if not npcap_exists():
        msg_box(
            'elmoCut',
            'Npcap is not installed on your machine!' \
            '\nClick Ok to download.',
            icon
        )
        webbrowser('start "" "https://nmap.org/npcap/dist/npcap-1.10.exe"')
    
    # Check if another elmoCut process is running
    elif duplicate_elmocut():
        msg_box(
            'elmoCut',
            'elmoCut is already running!',
            icon
        )
        bring_elmocut_tofront()
    
    # Run the GUI
    else:
        GUI = ElmoCut()
        GUI.show()
        GUI.resizeEvent()

        GUI.scanner = Scanner()
        GUI.killer = Killer()

        # Requires As Admin
        GUI.scanner.flush_arp()

        GUI.scanEasy()
        
        sys.exit(app.exec_())