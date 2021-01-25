from PyQt5.QtCore import QThread, pyqtSignal

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