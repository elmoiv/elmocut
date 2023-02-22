from PyQt5.QtWidgets import QMainWindow
# from PyQt5.QtCore import pyqtSignal, QEvent, QObject
from PyQt5.QtGui import QPixmap

from ui.ui_about import Ui_MainWindow
from tools.qtools import clickable
from tools.utils import goto
from assets import twitter_icon, linkedin_icon, github_icon, reddit_icon, app_icon

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
            (self.lblTwitter,  twitter_icon,  self.twitter),
            (self.lblLinkedIn, linkedin_icon, self.linkedin),
            (self.lblGitHub,   github_icon,   self.github),
            (self.lblReddit,   reddit_icon,   self.reddit)
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

    twitter    = lambda self: goto('https://twitter.com/___xpy___')
    linkedin   = lambda self: goto('https://www.linkedin.com/in/elmoiv/')
    github     = lambda self: goto('https://github.com/elmoiv')
    reddit     = lambda self: goto('https://www.reddit.com/user/elmoiv')
    github_app = lambda self: goto('https://github.com/elmoiv/elmocut')
