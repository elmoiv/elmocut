from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox as QMsg

class Buttons:
    CANCEL = QMsg.Cancel
    YES    = QMsg.Yes
    NO     = QMsg.No
    OK     = QMsg.Ok

class MsgType:
    INFO     = QMsg.information
    WARN     = QMsg.warning
    CRITICAL = QMsg.critical

class MsgIcon:
    INFO     = QMsg.Information
    WARN     = QMsg.Warning
    CRITICAL = QMsg.Critical

def colored_item(elmnt, c1, c2):
    """
    Add colors to Table rows
    """
    elmnt.setBackground(QColor(c1))
    elmnt.setForeground(QColor(c2))

def msg_box(title, text, window_icon, icon, buttons=Buttons.OK):
    """
    Main app independent QMessageBox
    """
    msg = QMsg()
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setWindowIcon(icon)
    msg.setIcon(window_icon)
    msg.setStandardButtons(buttons)
    return msg.exec_()
