from PyQt5.QtCore import QThread, pyqtSignal

class ScanThread(QThread):
    # Progress Bar value signal
    progress = pyqtSignal(int)

    # self.run() finish signal
    thread_finished_signal = pyqtSignal(bool)

    def __init__(self):
        QThread.__init__(self)

        self.scanner = None
        self.scan_type = None

    def run(self):
        # Execute arp of ping scan
        [
            self.easy,
            self.hard
        ][
            self.scan_type
        ]()

        # Emit show devices func to the thread finished reciever
        self.thread_finished_signal.emit(True)
    
    def easy(self):
        # Fake progress cause Scapy can't handle QThread Signals
        self.scanner.arp_scan()
    
    def hard(self):
        # self.pinging_watcher() will use progress signal
        # to update progress bar in GUI
        self.scanner.ping_scan(self.progress.emit)
        self.scanner.arping_cache()