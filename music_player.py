import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QFileDialog, QSlider,
                            QLabel, QListWidget)
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import os

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Музыкальный плеер")
        self.setGeometry(100, 100, 600, 400)

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected)
        layout.addWidget(self.playlist_widget)

        controls_layout = QHBoxLayout()
        
        self.play_button = QPushButton("Старт")
        self.play_button.clicked.connect(self.play_pause)
        controls_layout.addWidget(self.play_button)
        
        self.prev_button = QPushButton("Пред")
        self.prev_button.clicked.connect(self.play_previous)
        controls_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton("След")
        self.next_button.clicked.connect(self.play_next)
        controls_layout.addWidget(self.next_button)
        
        self.add_button = QPushButton("Добавить музыку")
        self.add_button.clicked.connect(self.add_music)
        controls_layout.addWidget(self.add_button)
        
        layout.addLayout(controls_layout)

        slider_layout = QHBoxLayout()
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.sliderMoved.connect(self.set_position)
        self.time_label = QLabel("0:00 / 0:00")
        slider_layout.addWidget(self.time_slider)
        slider_layout.addWidget(self.time_label)
        layout.addLayout(slider_layout)

        volume_layout = QHBoxLayout()
        volume_label = QLabel("Громкость:")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.audio_output.setVolume(0.7)
        self.volume_slider.valueChanged.connect(self.change_volume)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        layout.addLayout(volume_layout)

        self.playlist = []
        self.current_index = -1
        self.load_playlist()

        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)
        self.player.playbackStateChanged.connect(self.state_changed)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_position)
        self.update_timer.start(1000)
    
    def load_playlist(self):
        try:
            with open('last_playlist.json', 'r') as f:
                self.playlist = json.load(f)
                for song in self.playlist:
                    self.playlist_widget.addItem(os.path.basename(song))
        except FileNotFoundError:
            pass
    
    def save_playlist(self):
        with open('last_playlist.json', 'w') as f:
            json.dump(self.playlist, f)
    
    def add_music(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Music Files",
            "",
            "Music Files (*.mp3 *.wav *.ogg)"
        )
        for file in files:
            if file not in self.playlist:
                self.playlist.append(file)
                self.playlist_widget.addItem(os.path.basename(file))
        self.save_playlist()
    
    def play_selected(self, item):
        self.current_index = self.playlist_widget.row(item)
        self.play_current()
    
    def play_current(self):
        if 0 <= self.current_index < len(self.playlist):
            self.player.setSource(QUrl.fromLocalFile(self.playlist[self.current_index]))
            self.player.play()
            self.play_button.setText("Пауза")
    
    def play_pause(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_button.setText("Старт")
        else:
            if self.current_index == -1 and self.playlist:
                self.current_index = 0
            self.play_current()
    
    def play_next(self):
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.play_current()
    
    def play_previous(self):
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.play_current()
    
    def change_volume(self, value):
        self.audio_output.setVolume(value / 100.0)
    
    def set_position(self, position):
        self.player.setPosition(position)
    
    def position_changed(self, position):
        self.time_slider.setValue(position)
        self.update_time_label(position)
    
    def duration_changed(self, duration):
        self.time_slider.setRange(0, duration)
        self.update_time_label(self.player.position())
    
    def state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self.play_next()
    
    def update_position(self):
        self.update_time_label(self.player.position())
    
    def update_time_label(self, position):
        duration = self.player.duration()
        position_time = self.format_time(position)
        duration_time = self.format_time(duration)
        self.time_label.setText(f"{position_time} / {duration_time}")
    
    def format_time(self, ms):
        s = int(ms / 1000)
        m = int(s / 60)
        s = s % 60
        return f"{m}:{s:02d}"

def main():
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()