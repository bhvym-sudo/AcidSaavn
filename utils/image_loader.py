from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QSizePolicy, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont, QPixmap
import requests

class ImageLoader(QThread):
    imageLoaded = pyqtSignal(QPixmap, object)
    
    def __init__(self, image_url, song_card):
        super().__init__()
        self.image_url = image_url
        self.song_card = song_card
    
    def run(self):
        try:
            if self.image_url:
                response = requests.get(self.image_url, timeout=10)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.imageLoaded.emit(pixmap, self.song_card)
        except Exception as e:
            print(f"Failed to load image: {e}")
