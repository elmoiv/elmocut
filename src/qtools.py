from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox as QMsg
from assets import app_icon

CANCEL = QMsg.Cancel
YES = QMsg.Yes
NO = QMsg.No
OK = QMsg.Ok

def colored_item(elmnt, c1, c2):
    """
    Add colors to Table rows
    """
    elmnt.setBackground(QColor(c1))
    elmnt.setForeground(QColor(c2))

def msg_box(title, text, icon, buttons=OK):
    """
    Main app independent QMessageBox
    """
    msg = QMsg()
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setWindowIcon(icon)
    msg.setStandardButtons(buttons)
    return msg.exec_()