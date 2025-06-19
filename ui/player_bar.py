from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSlider, QFrame
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
import requests

CHARCOAL = "#1E3B4C"
CERULEAN = "#156F89"
NIGHT = "#101012"
RICH_BLACK = "#11151A"
PAYNES_GRAY = "#20637D"

class PlayerBar(QFrame):
    playPauseClicked = pyqtSignal()
    positionChanged = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.current_song = None
        self.is_playing = False
        self.duration = 0
        self.position = 0
        self.seeking = False
        self.setup_ui()

    def setup_ui(self):
        self.setFixedHeight(80)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {RICH_BLACK};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)

        self.album_art = QLabel()
        self.album_art.setFixedSize(60, 60)
        self.album_art.setStyleSheet(f"""
            QLabel {{
                background-color: {CHARCOAL};
                border-radius: 44px;
            }}
        """)
        self.album_art.setAlignment(Qt.AlignCenter)
        self.album_art.setText("♪")
        layout.addWidget(self.album_art)

        song_info_layout = QVBoxLayout()
        song_info_layout.setSpacing(2)

        self.song_title = QLabel("No song playing")
        self.song_title.setFont(QFont("Arial", 11, QFont.Bold))
        self.song_title.setStyleSheet("color: white; background: transparent;")

        self.song_artist = QLabel("")
        self.song_artist.setFont(QFont("Arial", 9))
        self.song_artist.setStyleSheet("color: #aaa; background: transparent;")

        song_info_layout.addWidget(self.song_title)
        song_info_layout.addWidget(self.song_artist)
        layout.addLayout(song_info_layout)

        layout.addStretch()

        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(5)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.setFixedSize(45, 45)
        self.play_pause_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CERULEAN};
                border: none;
                border-radius: 22px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {PAYNES_GRAY};
            }}
            QPushButton:pressed {{
                background-color: {CHARCOAL};
            }}
        """)
        self.play_pause_btn.clicked.connect(self.playPauseClicked.emit)
        buttons_layout.addWidget(self.play_pause_btn)

        controls_layout.addLayout(buttons_layout)

        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)

        self.current_time = QLabel("0:00")
        self.current_time.setFont(QFont("Arial", 8))
        self.current_time.setStyleSheet("color: #aaa; background: transparent;")
        self.current_time.setFixedWidth(35)
        progress_layout.addWidget(self.current_time)

        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(1000)
        self.progress_slider.setValue(0)
        self.progress_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: none;
                height: 4px;
                background: {CHARCOAL};
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {CERULEAN};
                border: none;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }}
            QSlider::handle:horizontal:hover {{
                background: white;
            }}
            QSlider::sub-page:horizontal {{
                background: {CERULEAN};
                border-radius: 2px;
            }}
        """)
        self.progress_slider.sliderPressed.connect(self.on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self.on_slider_released)
        self.progress_slider.valueChanged.connect(self.on_slider_moved)
        progress_layout.addWidget(self.progress_slider)

        self.total_time = QLabel("0:00")
        self.total_time.setFont(QFont("Arial", 8))
        self.total_time.setStyleSheet("color: #aaa; background: transparent;")
        self.total_time.setFixedWidth(35)
        progress_layout.addWidget(self.total_time)

        controls_layout.addLayout(progress_layout)
        layout.addLayout(controls_layout)

        layout.addStretch()

        self.hide()

    def set_song(self, song_data):
        self.current_song = song_data
        self.song_title.setText(song_data.get('title', 'Unknown Title')[:40])
        self.song_artist.setText(song_data.get('subtitle', 'Unknown Artist')[:50])
        self.load_album_art(song_data.get('image', ''))
        self.show()

    def load_album_art(self, image_url):
        if image_url:
            try:
                response = requests.get(image_url, timeout=5)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.album_art.setPixmap(pixmap)
                    return
            except:
                pass
        self.album_art.clear()
        self.album_art.setText("♪")

    def set_playing(self, playing):
        self.is_playing = playing
        if playing:
            self.play_pause_btn.setText("||")
        else:
            self.play_pause_btn.setText("▶")

    def set_duration(self, duration_seconds):
        self.duration = duration_seconds
        self.total_time.setText(self.format_time(duration_seconds))

    def set_position(self, position_seconds):
        if not self.seeking:
            self.position = position_seconds
            self.current_time.setText(self.format_time(position_seconds))
            if self.duration > 0:
                progress = int((position_seconds / self.duration) * 1000)
                self.progress_slider.setValue(progress)

    def on_slider_pressed(self):
        self.seeking = True

    def on_slider_released(self):
        if self.duration > 0:
            new_position = (self.progress_slider.value() / 1000.0) * self.duration
            self.position = new_position
            self.positionChanged.emit(new_position)
        self.seeking = False

    def on_slider_moved(self, value):
        if self.seeking and self.duration > 0:
            new_position = (value / 1000.0) * self.duration
            self.current_time.setText(self.format_time(new_position))

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"

    def reset(self):
        self.current_song = None
        self.is_playing = False
        self.duration = 0
        self.position = 0
        self.song_title.setText("No song playing")
        self.song_artist.setText("")
        self.current_time.setText("0:00")
        self.total_time.setText("0:00")
        self.progress_slider.setValue(0)
        self.play_pause_btn.setText("▶")
        self.album_art.clear()
        self.album_art.setText("♪")
        self.hide()
