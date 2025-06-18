from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QSizePolicy, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, QTimer
from core.token_module import get_stream_url
try:
    from ffpyplayer.player import MediaPlayer
    AUDIO_AVAILABLE = True
except ImportError:
    print("Warning: ffpyplayer not available. Audio playback disabled.")
    AUDIO_AVAILABLE = False

class PlayWorker(QThread):
    playbackStarted = pyqtSignal(float)
    playbackFailed = pyqtSignal(str)
    positionUpdate = pyqtSignal(float)
    playbackEnded = pyqtSignal()
    
    def __init__(self, song_data, query, start_position=0):
        super().__init__()
        self.song_data = song_data
        self.should_stop = False
        self.should_pause = False
        self.query = query
        self.start_position = start_position
        self.player = None
        self.duration = 0
    
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
            
            while not self.should_stop:
                if self.should_pause:
                    self.player.set_pause(True)
                    while self.should_pause and not self.should_stop:
                        self.msleep(100)
                    if not self.should_stop:
                        self.player.set_pause(False)
                
                frame, val = self.player.get_frame()
                if val == 'eof':
                    self.playbackEnded.emit()
                    break
                elif frame is not None:
                    if self.duration == 0:
                        try:
                            metadata = self.player.get_metadata()
                            if metadata and 'duration' in metadata:
                                self.duration = metadata['duration']
                            else:
                                duration_str = self.song_data.get('duration', '180')
                                try:
                                    if ':' in duration_str:
                                        parts = duration_str.split(':')
                                        self.duration = int(parts[0]) * 60 + int(parts[1])
                                    else:
                                        self.duration = int(duration_str)
                                except:
                                    self.duration = 180
                        except:
                            duration_str = self.song_data.get('duration', '180')
                            try:
                                if ':' in duration_str:
                                    parts = duration_str.split(':')
                                    self.duration = int(parts[0]) * 60 + int(parts[1])
                                else:
                                    self.duration = int(duration_str)
                            except:
                                self.duration = 180
                        
                        if self.start_position > 0:
                            self.player.seek(self.start_position)
                        
                        self.playbackStarted.emit(self.duration)
                    
                    current_time = self.player.get_pts()
                    if current_time is not None:
                        self.positionUpdate.emit(current_time)
                
                self.msleep(100)
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
            except:
                pass