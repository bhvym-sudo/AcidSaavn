from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QGridLayout, QPushButton
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
import requests
from core.newrelease_module import get_new_releases

CHARCOAL = "#1E3B4C"
CERULEAN = "#156F89"
NIGHT = "#101012"
RICH_BLACK = "#11151A"
PAYNES_GRAY = "#20637D"

class FetchNewReleasesWorker(QThread):
    data_fetched = pyqtSignal(list)
    
    def run(self):
        songs = get_new_releases()
        self.data_fetched.emit(songs)

class HomePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 0)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"background-color: {RICH_BLACK}; border: none;")
        self.content_widget = QWidget()
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setSpacing(25)
        self.scroll.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll)

        self.loading_label = QLabel("Fetching latest releases...")
        self.loading_label.setStyleSheet("color: #aaa; font-size: 14px;")
        self.grid_layout.addWidget(self.loading_label, 0, 0)
        
        self.fetch_thread = FetchNewReleasesWorker()
        self.fetch_thread.data_fetched.connect(self.display_songs)
        self.fetch_thread.start()

    def display_songs(self, songs):
        self.loading_label.hide()
        row, col = 0, 0
        for song in songs:
            card = self.create_song_card(song)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= 4:
                row += 1
                col = 0

    def create_song_card(self, song_data):
        card = QWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignTop)

        card.setStyleSheet(f"""
            QWidget {{
                background-color: {NIGHT};
                border-radius: 12px;
            }}
            QWidget:hover {{
                background-color: {CHARCOAL};
            }}
        """)
        card.setFixedSize(180, 300)

        image_wrapper = QWidget()
        image_wrapper.setFixedSize(130, 130)
        image_layout = QVBoxLayout(image_wrapper)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setAlignment(Qt.AlignCenter)

        image_label = QLabel()
        image_label.setFixedSize(130, 130)
        image_label.setStyleSheet("border-radius: 8px; background-color: transparent; padding: 16px 0px;")
        try:
            image = requests.get(song_data['image'], timeout=5)
            pix = QPixmap()
            pix.loadFromData(image.content)
            pix = pix.scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(pix)
        except:
            image_label.setText("♪")
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet(f"color: white; background-color: {CHARCOAL};")

        image_layout.addWidget(image_label)
        layout.addWidget(image_wrapper, alignment=Qt.AlignCenter)

        title = QLabel(song_data['title'])
        title.setFont(QFont("Arial", 10, QFont.Bold))
        title.setStyleSheet("color: white; padding: 0px 6px; background-color: transparent;")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignCenter)
        if len(title.text()) > 30:
            title.setText(title.text()[:27] + "...")
        layout.addWidget(title)

        subtitle = QLabel(song_data['subtitle'])
        subtitle.setFont(QFont("Arial", 9))
        subtitle.setStyleSheet("color: gray; padding: 0px 6px; background-color: transparent;")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        if len(subtitle.text()) > 35:
            subtitle.setText(subtitle.text()[:32] + "...")
        layout.addWidget(subtitle)

        play_button = QPushButton("▶")
        play_button.setFixedSize(36, 36)
        play_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {CERULEAN};
                border: none;
                border-radius: 18px;
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
        play_button.clicked.connect(lambda: self.main_window.play_song_from_card(song_data, None))
        layout.addWidget(play_button, alignment=Qt.AlignCenter)

        return card

