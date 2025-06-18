import sys
import threading
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QSizePolicy, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont, QPixmap
from core.search_module import search_jiosaavn
from core.token_module import get_stream_url
from core.downloader import download_song
from ui.player_bar import PlayerBar
from utils.image_loader import ImageLoader
from utils.search_worker import SearchWorker
from utils.player_worker import PlayWorker
from utils.song_card import SongCard



CHARCOAL = "#1E3B4C"
CERULEAN = "#156F89"
NIGHT = "#101012"
RICH_BLACK = "#11151A"
PAYNES_GRAY = "#20637D"





class AcidSaavnGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AcidSaavn")
        self.setFixedSize(1300,780)
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
        self.current_song_data = None
        self.song_cards = []
        self.is_paused = False
        self.current_position = 0
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.setup_ui()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 0)
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
        
        self.player_bar = PlayerBar()
        self.player_bar.playPauseClicked.connect(self.toggle_playback)
        self.player_bar.positionChanged.connect(self.seek_to_position)
        main_layout.addWidget(self.player_bar)

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

    def play_song_from_card(self, song_data, card):
        if self.current_playing_card == card and self.current_song_data == song_data:
            self.toggle_playback()
            return
        
        self.stop_song()
        for song_card in self.song_cards:
            if not song_card.is_deleted:
                song_card.reset_play_state()
        
        self.current_playing_card = card
        self.current_song_data = song_data
        self.current_position = 0
        self.is_paused = False
        
        card.set_playing_state(True)
        self.player_bar.set_song(song_data)
        self.player_bar.set_playing(True)
        self.start_playback()

    def start_playback(self):
        if not self.current_song_data:
            return

        query = self.search_bar.text().strip()
        self.status_label.setText(f"Loading: {self.current_song_data['title']}")

        duration_raw = self.current_song_data.get("duration", "180")
        if isinstance(duration_raw, str) and ":" in duration_raw:
            mins, secs = map(int, duration_raw.split(":"))
            self.current_song_data["duration"] = mins * 60 + secs
        else:
            self.current_song_data["duration"] = float(duration_raw)

        self.play_worker = PlayWorker(self.current_song_data, query=query, start_position=self.current_position)
        self.play_worker.playbackStarted.connect(self.on_playback_started)
        self.play_worker.playbackFailed.connect(self.on_playback_failed)
        self.play_worker.positionUpdate.connect(self.on_position_update)
        self.play_worker.playbackEnded.connect(self.on_playback_ended)
        self.play_worker.start()


    def toggle_playback(self):
        if not self.current_song_data:
            return
        
        if self.is_paused:
            self.resume_playback()
        else:
            self.pause_playback()

    def pause_playback(self):
        if self.play_worker and self.play_worker.isRunning():
            self.play_worker.pause()
            self.is_paused = True
            self.player_bar.set_playing(False)
            if self.current_playing_card and not self.current_playing_card.is_deleted:
                self.current_playing_card.set_playing_state(False)
            self.status_label.setText(f"Paused: {self.current_song_data['title']}")

    def resume_playback(self):
        if self.play_worker and self.play_worker.isRunning():
            self.play_worker.resume()
            self.is_paused = False
            self.player_bar.set_playing(True)
            if self.current_playing_card and not self.current_playing_card.is_deleted:
                self.current_playing_card.set_playing_state(True)
            self.status_label.setText(f"Playing: {self.current_song_data['title']}")


    def seek_to_position(self, position):
        self.current_position = position
        if self.play_worker and self.play_worker.isRunning():
            self.play_worker.seek(position)
        self.player_bar.set_position(position)

    def on_playback_started(self, duration):
        self.player_bar.set_duration(duration)
        self.player_bar.set_playing(True)
        self.status_label.setText(f"Playing: {self.current_song_data['title']}")

    def on_playback_failed(self, error_message):
        if self.current_playing_card:
            self.current_playing_card.reset_play_state()
        self.player_bar.reset()
        self.current_playing_card = None
        self.current_song_data = None
        self.status_label.setText("Ready")
        self.show_error("Playback Error", error_message)

    def on_position_update(self, position):
        self.current_position = position
        self.player_bar.set_position(position)

    def on_playback_ended(self):
        self.stop_song()
        self.status_label.setText("Playback finished")

    def stop_song(self):
        if self.play_worker and self.play_worker.isRunning():
            self.play_worker.stop()
            self.play_worker.wait()
        if self.current_playing_card:
            self.current_playing_card.reset_play_state()
        self.player_bar.reset()
        self.current_playing_card = None
        self.current_song_data = None
        self.current_position = 0
        self.is_paused = False
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
                    color: {PAYNES_GRAY};
                }}
                QMessageBox QPushButton {{
                    background-color: {CERULEAN};
                    color: {PAYNES_GRAY};
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