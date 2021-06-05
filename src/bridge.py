from PyQt5.QtCore import QThread, pyqtSignal
from requests import get

class ScanThread(QThread):
    # Progress Bar value signal
    progress = pyqtSignal(int)
    thread_finished = pyqtSignal(bool)

    def __init__(self):
        QThread.__init__(self)

        self.scanner = None
        self.scan_type = None

    def run(self):
        # Execute arp or ping scan
        if self.scan_type:
            self.hard()
        else:
            self.easy()

        # Emit show devices func to the thread finished reciever
        self.thread_finished.emit(True)
    
    def easy(self):
        # Fake progress cause Scapy can't handle QThread Signals
        self.scanner.arp_scan()
    
    def hard(self):
        # self.pinging_watcher() will use progress signal
        # to update progress bar in GUI
        self.scanner.qt_progress_signal = self.progress.emit
        self.scanner.ping_scan()
        self.scanner.arping_cache()

class UpdateThread(QThread):
    thread_finished = pyqtSignal(bool)

    def __init__(self):
        QThread.__init__(self)
        self.prompt_if_latest = True # Show "You have the latest version" msg
        self.github_version = 'None'
        self.url = 'https://github.com/elmoiv/elmocut/releases/latest'

    def run(self):
        try:
            redirect = get(self.url)
            self.github_version = redirect.url.split('/')[-1]
        except Exception as e:
            print('Error at Update Thread:', e)

        self.thread_finished.emit(True)