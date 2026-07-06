from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QPalette, QColor
from networking.nicknames import Nicknames
from tools.qtools import  MsgType
from ui.ui_device import Ui_MainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidgetItem
from networking.diverter import ElmoDivert
from models.device import Device
from datetime import datetime

class DeviceWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, elmocut, icon):
        super().__init__()
        self.elmocut = elmocut
        self.device: Device = None
        self.current_row = -1
        self.__nicknames = Nicknames()

        # Setup UI
        self.icon = icon
        self.setWindowIcon(icon)
        self.setupUi(self)
        # self.setFixedSize(self.size())

        self.setPlaceholderColor()
        self.tableUrlWatch.setColumnCount(3)
        self.tableUrlWatch.verticalHeader().setVisible(False)
        self.tableUrlWatch.setHorizontalHeaderLabels(["Timestamp", "Protocol", "Hostname"])
        self.tableUrlWatch.horizontalHeader().setStretchLastSection(True)

        self.btnChange.clicked.connect(self.changeName)
        self.btnReset.clicked.connect(self.resetName)
        # On Enter Pressed
        self.txtNickname.returnPressed.connect(self.changeName)
        self.btnStopWatch.setEnabled(False)
        self.btnStartWatch.setEnabled(True)

        self.btnStartWatch.clicked.connect(self.start_watching)
        self.btnStopWatch.clicked.connect(self.stop_watching)

    def start_watching(self):
        if self.device.mac in self.elmocut.killer.killed:
            MsgType.WARN(
                self,
                'Cannot Watch Device!',
                'This device is currently killed.\nUnkill it first to watch its traffic.'
            )
            return  # Stop button stays disabled, nothing else changes

        if not self.elmocut.ip_forwarding_enabled:
            if not self.elmocut.request_enable_ip_forwarding():
                return

        if self.device.mac in self.elmocut.watched_devices:
            print(f"[Warning] {self.device.ip} is already being watched.")
            return
        self.btnStopWatch.setEnabled(True)
        self.btnStartWatch.setEnabled(False)
        # Create a fresh ElmoDivert instance for this window
        divert = ElmoDivert(
            victim_ip=self.device.ip,
            victim_mac=self.device.mac,
            gateway_ip=self.elmocut.scanner.router_ip,
            router_mac=self.elmocut.scanner.router_mac,
            my_mac=self.elmocut.scanner.my_mac,
            interface=self.elmocut.scanner.iface.name,
            callback=self.on_device_watched
        )

        self.elmocut.watched_devices[self.device.mac] = divert
        divert.start()
        self.elmocut.showDevices()
        self.hide()
        self.show()
        # self.elmocut.refreshDeviceRow(self.device.mac)
    
    def on_device_watched(self, hostname, protocol):
        """
        Callback function to handle data received from the watched device.
        """
        if hostname is None and protocol is None:
            # The divert has stopped, update the UI accordingly
            self.btnStopWatch.setEnabled(False)
            self.btnStartWatch.setEnabled(True)
            return
        print(f"[DeviceWindow] Data received from {self.device.name} ({self.device.ip}): {hostname}")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Callback will be always calling i want the table to show max of
        # 100 rows at a time and every new callback is added at top
        self.tableUrlWatch.insertRow(0)
        self.tableUrlWatch.setItem(0, 0, QTableWidgetItem(now))
        self.tableUrlWatch.setItem(0, 1, QTableWidgetItem(protocol))
        self.tableUrlWatch.setItem(0, 2, QTableWidgetItem(hostname))

        self.tableUrlWatch.setColumnWidth(0, 160)
        self.tableUrlWatch.setColumnWidth(1, 100) 

        if self.tableUrlWatch.rowCount() > 2000:
            self.tableUrlWatch.removeRow(2000)

    def stop_watching(self):
        self.btnStopWatch.setEnabled(False)
        if self.device.mac in self.elmocut.watched_devices:
            divert = self.elmocut.watched_devices[self.device.mac]
            divert.stop() 
            del self.elmocut.watched_devices[self.device.mac]
            self.elmocut.showDevices()
    
    def load(self, device, current_row):
        self.setWindowTitle(f'elmoCut - {device.name or device.ip} ({device.ip})')
        self.lblIP.setText(device.ip)
        self.lblMAC.setText(device.mac)
        if device.name != '-':
            self.txtNickname.setText(device.name)
        else:
            self.txtNickname.setText('')
        self.current_row = current_row
        self.device = device

        is_watching = device.mac in self.elmocut.watched_devices
        self.btnStartWatch.setEnabled(not is_watching)          
        self.btnStopWatch.setEnabled(is_watching)               

    def setPlaceholderColor(self):
        pal = self.txtNickname.palette()
        pal.setColor(QPalette.ColorRole.PlaceholderText, QColor('#B5B5B5'))
        self.txtNickname.setPalette(pal)
        
    def changeName(self):
        name = self.txtNickname.text().strip()
        if not name or name == '-':
            name = self.device.name
            return self.instantApplyChanges(name)
        self.__nicknames.set_name(self.device.mac, name)
        self.instantApplyChanges(name)
    
    def resetName(self):
        name = '-'
        self.__nicknames.reset_name(self.device.mac)
        self.txtNickname.setText('')
        self.instantApplyChanges(name)

    def instantApplyChanges(self, name):
        self.device.name = name
        self.elmocut.fillTableRow(self.current_row, self.device)
        self.close()

    def showEvent(self, event):
        # self.tableUrlWatch.setRowCount(0)
        self.tableUrlWatch.scrollToTop()
        self.setStyleSheet(self.elmocut.styleSheet())
        event.accept()
    
    def closeEvent(self, a0):
        """
        Closing the window just hides it — watching (if active) keeps
        running in the background. It only fully stops when the user
        clicks 'Stop Watching', or when elmoCut itself closes.
        """
        a0.ignore()
        self.hide()