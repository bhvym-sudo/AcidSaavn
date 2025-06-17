import sys
import threading
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QSizePolicy, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont, QPixmap
from core.search_module import search_jiosaavn
from core.token_module import get_stream_url
from core.downloader import download_song

try:
    from ffpyplayer.player import MediaPlayer
    AUDIO_AVAILABLE = True
except ImportError:
    print("Warning: ffpyplayer not available. Audio playback disabled.")
    AUDIO_AVAILABLE = False

CHARCOAL = "#1E3B4C"
CERULEAN = "#156F89"
NIGHT = "#101012"
RICH_BLACK = "#11151A"
PAYNES_GRAY = "#20637D"

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

class PlayWorker(QThread):
    playbackStarted = pyqtSignal()
    playbackFailed = pyqtSignal(str)
    
    def __init__(self, song_data, query):
        super().__init__()
        self.song_data = song_data
        self.should_stop = False
        self.query = query
    
    def run(self):
        try:
            stream_url = get_stream_url(self.song_data['encrypted_media_url'], query=self.query)
            if not stream_url:
                self.playbackFailed.emit("Failed to get stream URL")
                return
            if not AUDIO_AVAILABLE:
                self.playbackFailed.emit("Audio player not available")
                return
            self.player = MediaPlayer(stream_url)
            self.playbackStarted.emit()
            while not self.should_stop:
                frame, val = self.player.get_frame()
                if val == 'eof':
                    break
                self.msleep(100)  
        except Exception as e:
            self.playbackFailed.emit(str(e))
    
    def stop(self):
        self.should_stop = True
        if hasattr(self, 'player'):
            try:
                self.player.close_player()
            except:
                pass

class SongCard(QFrame):
    def __init__(self, song_data, parent):
        super().__init__()
        self.song_data = song_data
        self.is_playing = False
        self.parent = parent
        self.image_loader = None
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
        if song_card == self:
            self.image_label.setPixmap(pixmap)
            self.image_label.setText("")
    
    def play_pause(self):
        if not self.is_playing:
            self.parent.play_song(self.song_data, self)
            self.play_btn.setText("||")
            self.is_playing = True
        else:
            self.parent.stop_song()
            self.play_btn.setText("▶")
            self.is_playing = False
    
    def download_song(self):
        self.parent.download_song(self.song_data)
    
    def reset_play_state(self):
        self.play_btn.setText("▶")
        self.is_playing = False

class AcidSaavnGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AcidSaavn")
        self.setFixedSize(1300,700)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {NIGHT};
                color: {NIGHT};
            }}
            QScrollArea {{
                background-color: {RICH_BLACK};
            }}
            QScrollBar:vertical {{
                background-color: {CHARCOAL};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #555;
                border-radius: 6px;
            }}
        """)
        self.search_worker = None
        self.play_worker = None
        self.current_playing_card = None
        self.song_cards = []
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.setup_ui()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        title_label = QLabel("AcidSaavn")
        title_label.setFont(QFont("Arial", 28, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {CERULEAN}; margin: 10px;")
        main_layout.addWidget(title_label)

        version_label = QLabel("Version - z2, made by bhvym")
        version_label.setFont(QFont("Arial", 9))
        version_label.setStyleSheet("color: gray; padding-right: 5px;")
        version_label.setAlignment(Qt.AlignRight)



        version_container = QHBoxLayout()
        version_container.addStretch()
        version_container.addWidget(version_label)

        main_layout.addLayout(version_container)
        
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for songs, artists, albums...")
        self.search_bar.setFixedHeight(40)
        self.search_bar.setStyleSheet(f"""
            QLineEdit {{
                background-color: {RICH_BLACK};
                border: 2px solid {CHARCOAL};
                border-radius: 20px;
                padding: 0 15px;
                font-size: 14px;
                color: white;
            }}
            QLineEdit:focus {{
                border-color: {CERULEAN};
            }}
        """)
        self.search_bar.returnPressed.connect(self.search)
        self.search_bar.textChanged.connect(self.on_text_changed)
        search_layout.addWidget(self.search_bar)
        
        
        main_layout.addLayout(search_layout)
        
        self.status_label = QLabel("Enter a search query to find music...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #aaa; font-size: 14px; margin: 10px;")
        main_layout.addWidget(self.status_label)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.results_widget = QWidget()
        self.results_widget.setStyleSheet(f"background-color: {RICH_BLACK};")
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(5)
        self.results_layout.addStretch()  
        
        self.scroll_area.setWidget(self.results_widget)
        main_layout.addWidget(self.scroll_area)

    def on_text_changed(self):
        self.search_timer.stop()
        query = self.search_bar.text().strip()
        if query:
            self.search_timer.start(300)
        else:
            self.clear_results()
            self.status_label.setText("Enter a search query to find music...")

    def perform_search(self):
        query = self.search_bar.text().strip()
        if query:
            self.clear_results()
            self.status_label.setText(f"Searching for '{query}'...")
            self.stop_song()
            if self.search_worker and self.search_worker.isRunning():
                self.search_worker.terminate()
                self.search_worker.wait()
            self.search_worker = SearchWorker(query)
            self.search_worker.songFound.connect(self.add_song_result)
            self.search_worker.searchCompleted.connect(self.on_search_completed)
            self.search_worker.searchFailed.connect(self.on_search_failed)
            self.search_worker.start()

    def search(self):
        self.search_timer.stop()
        self.perform_search()

    def clear_results(self):
        for card in self.song_cards:
            card.deleteLater()
        self.song_cards.clear()

    def add_song_result(self, song_data):
        song_card = SongCard(song_data, self)
        self.results_layout.insertWidget(self.results_layout.count() - 1, song_card)
        self.song_cards.append(song_card)

    def on_search_completed(self):

        count = len(self.song_cards)
        self.status_label.setText(f"Found {count} results" if count > 0 else "No results found")

    def on_search_failed(self, error_message):
        self.status_label.setText(f"Search failed: {error_message}")
        self.show_error("Search Error", error_message)

    def play_song(self, song_data, card):
        query = self.search_bar.text().strip()
        self.stop_song()
        for song_card in self.song_cards:
            song_card.reset_play_state()
        self.current_playing_card = card
        self.status_label.setText(f"Loading: {song_data['title']}")
        self.play_worker = PlayWorker(song_data, query=query)
        self.play_worker.playbackStarted.connect(lambda: self.on_playback_started(song_data))
        self.play_worker.playbackFailed.connect(self.on_playback_failed)
        self.play_worker.start()

    def on_playback_started(self, song_data):
        self.status_label.setText(f"Playing: {song_data['title']}")

    def on_playback_failed(self, error_message):
        if self.current_playing_card:
            self.current_playing_card.reset_play_state()
        self.status_label.setText("Ready")
        self.show_error("Playback Error", error_message)

    def stop_song(self):
        if self.play_worker and self.play_worker.isRunning():
            self.play_worker.stop()
            self.play_worker.wait()
        if self.current_playing_card:
            self.current_playing_card.reset_play_state()
            self.current_playing_card = None
        self.status_label.setText("Ready")

    def download_song(self, song_data):
        try:
            query = self.search_bar.text().strip()
            self.status_label.setText(f"Downloading: {song_data['title']}")
            stream_url = get_stream_url(song_data['encrypted_media_url'], query=query)
            if not stream_url:
                self.show_error("Download Error", "Failed to get stream URL")
                return
            
            filename = f"{song_data['title']} - {song_data['subtitle']}.mp3".replace('/', '-')
            response = requests.get(stream_url, stream=True)
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
            self.status_label.setText(f"Downloaded: {filename}")
            msg = QMessageBox(self)
            msg.setWindowTitle("Download Complete")
            msg.setText(f"Song downloaded:\n{filename}")
            msg.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {RICH_BLACK};
                    color: white;
                }}
                QMessageBox QPushButton {{
                    background-color: {CERULEAN};
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 5px;
                }}
            """)
            msg.exec_()
        except Exception as e:
            self.show_error("Download Error", str(e))


    def show_error(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {RICH_BLACK};
                color: white;
            }}
            QMessageBox QPushButton {{
                background-color: #D32F2F;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
            }}
        """)
        msg.exec_()

    def closeEvent(self, event):
        self.stop_song()
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.terminate()
            self.search_worker.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AcidSaavnGUI()
    window.show()
    sys.exit(app.exec_())