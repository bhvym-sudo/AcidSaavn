from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QSizePolicy, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont, QPixmap
from utils.image_loader import ImageLoader

CHARCOAL = "#1E3B4C"
CERULEAN = "#156F89"
NIGHT = "#101012"
RICH_BLACK = "#11151A"
PAYNES_GRAY = "#20637D"

class SongCard(QFrame):
    def __init__(self, song_data, parent):
        super().__init__()
        self.song_data = song_data
        self.is_playing = False
        self.parent = parent
        self.image_loader = None
        self.is_deleted = False
        self.setup_ui()
        self.load_image()
    
    def setup_ui(self):
        self.setFixedHeight(80)
        self.setStyleSheet(f"""
            QFrame {{ 
                background-color: {RICH_BLACK}; 
                border-radius: 12px; 
                margin: 5px; 
            }}
            QFrame:hover {{
                background-color: {NIGHT};
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(60, 60)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #333;
                border-radius: 8px;
            }
        """)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("♪")
        layout.addWidget(self.image_label)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        self.title_label = QLabel(self.song_data.get('title', 'Unknown Title'))
        self.subtitle_label = QLabel(self.song_data.get('subtitle', 'Unknown Artist'))
        self.title_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.subtitle_label.setFont(QFont("Arial", 9))
        self.title_label.setStyleSheet("""
            background-color: transparent;
            color: white;
        """)

        self.subtitle_label.setStyleSheet("""
            background-color: transparent;
            color: gray;
        """)
        if len(self.title_label.text()) > 40:
            self.title_label.setText(self.title_label.text()[:37] + "...")
        if len(self.subtitle_label.text()) > 50:
            self.subtitle_label.setText(self.subtitle_label.text()[:47] + "...")
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.subtitle_label)
        layout.addLayout(info_layout)
        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(40, 40)
        self.play_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CERULEAN};
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {PAYNES_GRAY};
            }}
            QPushButton:pressed {{
                background-color: {CHARCOAL};
            }}
        """)
        self.play_btn.clicked.connect(self.play_pause)
        button_layout.addWidget(self.play_btn)
        
        download_btn = QPushButton("⭣")
        download_btn.setFixedSize(40, 40)
        download_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CHARCOAL};
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #444;
            }}
        """)
        download_btn.clicked.connect(self.download_song)
        button_layout.addWidget(download_btn)
        
        layout.addLayout(button_layout)
    
    def load_image(self):
        image_url = self.song_data.get('image', '')
        if image_url:
            self.image_loader = ImageLoader(image_url, self)
            self.image_loader.imageLoaded.connect(self.on_image_loaded)
            self.image_loader.start()
    
    def on_image_loaded(self, pixmap, song_card):
        if song_card == self and not self.is_deleted:
            self.image_label.setPixmap(pixmap)
            self.image_label.setText("")
    
    def play_pause(self):
        self.parent.play_song_from_card(self.song_data, self)
    
    def download_song(self):
        self.parent.download_song(self.song_data)
    
    def set_playing_state(self, playing):
        if not self.is_deleted:
            self.is_playing = playing
            self.play_btn.setText("⏸" if playing else "▶")
    
    def reset_play_state(self):
        if not self.is_deleted:
            self.play_btn.setText("▶")
            self.is_playing = False
    
    def deleteLater(self):
        self.is_deleted = True
        if self.image_loader and self.image_loader.isRunning():
            self.image_loader.terminate()
            self.image_loader.wait()
        super().deleteLater()

