from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QPalette, QColor
from networking.nicknames import Nicknames
from ui.ui_device import Ui_MainWindow

class Device(QMainWindow, Ui_MainWindow):
    def __init__(self, elmocut, icon):
        super().__init__()
        self.elmocut = elmocut
        self.device = None
        self.current_row = -1
        self.__nicknames = Nicknames()

        # Setup UI
        self.icon = icon
        self.setWindowIcon(icon)
        self.setupUi(self)
        self.setFixedSize(self.size())

        self.setPlaceholderColor()
        
        self.btnChange.clicked.connect(self.changeName)
        self.btnReset.clicked.connect(self.resetName)
        # On Enter Pressed
        self.txtNickname.returnPressed.connect(self.changeName)
    
    def load(self, device, current_row):
        self.lblIP.setText(device['ip'])
        self.lblMAC.setText(device['mac'])
        if device['name'] != '-':
            self.txtNickname.setText(device['name'])
        else:
            self.txtNickname.setText('')
        self.current_row = current_row
        self.device = device

    def setPlaceholderColor(self):
        pal = self.txtNickname.palette()
        pal.setColor(QPalette.PlaceholderText, QColor('#B5B5B5'))
        self.txtNickname.setPalette(pal)
        
    def changeName(self):
        name = self.txtNickname.text().strip()
        if not name or name == '-':
            name = self.device['name']
            return self.instantApplyChanges(name)
        self.__nicknames.set_name(self.device['mac'], name)
        self.instantApplyChanges(name)
    
    def resetName(self):
        name = '-'
        self.__nicknames.reset_name(self.device['mac'])
        self.txtNickname.setText('')
        self.instantApplyChanges(name)

    def instantApplyChanges(self, name):
        self.device['name'] = name
        self.elmocut.fillTableRow(self.current_row, self.device)
        self.close()

    def showEvent(self, event):
        self.setStyleSheet(self.elmocut.styleSheet())
        event.accept()