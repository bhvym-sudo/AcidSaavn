from PyQt5.QtCore import QThread, pyqtSignal
from core.token_module import get_stream_url
import time

try:
    from ffpyplayer.player import MediaPlayer
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

class PlayWorker(QThread):
    playbackStarted = pyqtSignal(float)
    playbackFailed = pyqtSignal(str)
    positionUpdate = pyqtSignal(float)
    playbackEnded = pyqtSignal()

    def __init__(self, song_data, query, start_position=0):
        super().__init__()
        self.song_data = song_data
        self.query = query
        self.start_position = start_position
        self.should_stop = False
        self.should_pause = False
        self.player = None
        self.duration = float(song_data.get("duration", 180))
        self.position = 0
        self.start_time = None
        self.pause_time = None

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

            if self.start_position > 0:
                self.player.seek(self.start_position)

            self.start_time = time.time() - self.start_position
            self.playbackStarted.emit(self.duration)

            while not self.should_stop:
                if self.should_pause:
                    self.pause_time = time.time()
                    self.player.set_pause(True)
                    while self.should_pause and not self.should_stop:
                        time.sleep(0.1)
                    if not self.should_stop:
                        pause_duration = time.time() - self.pause_time
                        self.start_time += pause_duration
                        self.player.set_pause(False)

                current_time = time.time() - self.start_time
                if current_time >= self.duration:
                    self.playbackEnded.emit()
                    break

                self.positionUpdate.emit(current_time)
                time.sleep(0.1)

        except Exception as e:
            self.playbackFailed.emit(str(e))

    def stop(self):
        self.should_stop = True
        if self.player:
            try:
                self.player.close_player()
            except:
                pass

    def pause(self):
        self.should_pause = True

    def resume(self):
        self.should_pause = False

    def seek(self, position):
        if self.player:
            try:
                self.player.seek(position)
                self.start_time = time.time() - position
            except:
                pass
