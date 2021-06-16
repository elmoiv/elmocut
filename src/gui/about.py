from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal, QEvent, QObject
from PyQt5.QtGui import QPixmap

from ui.ui_about import Ui_MainWindow

from tools.utils import goto

from assets import facebook_icon, twitter_icon, linkedin_icon, github_icon, app_icon

def clickable(widget):
    class Filter(QObject):
        clicked = pyqtSignal()
        def eventFilter(self, obj, event):
            if obj == widget and \
               event.type() == QEvent.MouseButtonRelease and \
               obj.rect().contains(event.pos()):
                    self.clicked.emit()
                    return True
            return False
    
    _filter = Filter(widget)
    widget.installEventFilter(_filter)
    return _filter.clicked

class About(QMainWindow, Ui_MainWindow):
    def __init__(self, elmocut, icon):
        super().__init__()
        self.elmocut = elmocut

        # Setup UI
        self.icon = icon
        self.setWindowIcon(icon)
        self.setupUi(self)
        self.setFixedSize(self.size())

        self.social_labels = [
            (self.lblAppIcon,  app_icon,      self.github_app),
            (self.lblFacebook, facebook_icon, self.facebook),
            (self.lblTwitter,  twitter_icon,  self.twitter),
            (self.lblLinkedIn, linkedin_icon, self.linkedin),
            (self.lblGitHub,   github_icon,   self.github)
        ]

        for lbl, icon, url in self.social_labels:
            clickable(lbl).connect(url)
            self.setImage(lbl, icon)

        self.lblAppName.setText(f'elmoCut v{self.elmocut.version}')
        self.lblMyName.setText('Khaled El-Morshedy')
        self.lblNickName.setText('(elmoiv)')
    
    def showEvent(self, event):
        self.setStyleSheet(self.elmocut.styleSheet())
        event.accept()
    
    def setImage(self, label, icon):
        pix = QPixmap()
        pix.loadFromData(icon)
        label.setPixmap(pix)

    facebook   = lambda self: goto('https://www.facebook.com/elmoiv/')
    twitter    = lambda self: goto('https://twitter.com/___xpy___')
    linkedin   = lambda self: goto('https://www.linkedin.com/in/elmoiv/')
    github     = lambda self: goto('https://github.com/elmoiv')
    github_app = lambda self: goto('https://github.com/elmoiv/elmocut')
