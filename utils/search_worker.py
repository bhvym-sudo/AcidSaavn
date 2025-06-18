from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QSizePolicy, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont, QPixmap
from core.search_module import search_jiosaavn

class SearchWorker(QThread):
    songFound = pyqtSignal(dict)
    searchCompleted = pyqtSignal()
    searchFailed = pyqtSignal(str)
    
    def __init__(self, query):
        super().__init__()
        self.query = query
    
    def run(self):
        try:
            results = search_jiosaavn(self.query)
            if results:
                for song in results:
                    self.songFound.emit(song)
                self.searchCompleted.emit()
            else:
                self.searchFailed.emit("No results found")
        except Exception as e:
            self.searchFailed.emit(str(e))