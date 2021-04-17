from utils_gui import import_settings, export_settings, get_settings, \
                      is_admin, add_to_startup, remove_from_startup
from PyQt5.QtWidgets import QMainWindow
from qdarkstyle import load_stylesheet
from ui_settings import Ui_MainWindow
from qtools import MsgType, Buttons
from utils import goto

class Settings(QMainWindow, Ui_MainWindow):
    def __init__(self, elmocut, icon):
        super().__init__()
        self.elmocut = elmocut

        # Setup UI
        self.icon = icon
        self.setWindowIcon(icon)
        self.setupUi(self)
        self.setFixedSize(self.size())

        # Apply old settings on open
        self.currentSettings()

        self.sliderCount.valueChanged.connect(self.spinCount.setValue)
        self.spinCount.valueChanged.connect(self.sliderCount.setValue)
        self.btnApply.clicked.connect(self.Apply)
        self.btnDefaults.clicked.connect(self.Defaults)
        self.btnUpdate.clicked.connect(self.elmocut.update_thread.start)

    def Apply(self):
        exe_path = '\\'.join(__file__.split('\\')[:-1] + ['elmocut.exe'])

        count        = self.spinCount.value()
        is_dark      = self.rdbDark.isChecked()
        is_autostart = self.chkAutostart.isChecked()
        is_minimized = self.chkMinimized.isChecked()
        is_remember  = self.chkRemember.isChecked()
       
        if is_autostart:
            add_to_startup(exe_path)
        else:
            remove_from_startup()

        # Make sure that real-time killed devices are included
        # If its user's first time to apply remember option
        killed_from_json = get_settings('killed')
        killed_from_elmo = list(self.elmocut.killer.killed)
        killed_all = list(set(killed_from_json + killed_from_elmo)) * is_remember

        export_settings([is_dark, count, is_autostart, is_minimized, is_remember, killed_all])

        self.updateElmocutSettings()

        MsgType.INFO(
            self,
            'Apply Settings',
            'New settings have been applied.'
        )

    def Defaults(self):
        if MsgType.WARN(
            self,
            'Default settings',
            'All settings will be reset to default.\nAre you sure?',
            Buttons.YES | Buttons.NO
        ) == Buttons.NO:
            return
        export_settings()
        self.currentSettings()
        self.Apply()

    def updateElmocutSettings(self):
        s = import_settings()
        self.currentSettings()
        self.elmocut.minimize = s['minimized']
        self.elmocut.remember = s['remember']
        self.elmocut.scanner.device_count = s['count']
        self.elmocut.setStyleSheet(self.styleSheet())
        self.elmocut.about_window.setStyleSheet(self.styleSheet())

    def currentSettings(self):
        s = import_settings()
        if s['dark']:
            self.rdbDark.setChecked(True)
        else:
            self.rdbLight.setChecked(True)
        self.chkAutostart.setChecked(s['autostart'])
        self.chkMinimized.setChecked(s['minimized'])
        self.chkRemember.setChecked(s['remember'])
        self.spinCount.setValue(s['count'])
        self.sliderCount.setValue(s['count'])
        self.setStyleSheet(load_stylesheet() if s['dark'] else '')