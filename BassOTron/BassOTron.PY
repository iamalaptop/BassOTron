import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import numpy as np
from PIL import Image, ImageTk

class BassOTronApp:
    def __init__(self, master):
        self.master = master
        self.master.title("BassOTron")
        self.master.geometry("800x600")  # Set initial size
        self.master.resizable(True, True)

        # Initialize Pygame
        pygame.mixer.init()

        # Track state
        self.is_song_playing = False
        self.is_bass_playing = False
        self.current_sound = None
        self.file_path = ""  # Initialize file_path
        self.current_frequency = 440  # Default frequency

        # Load icons
        self.cd_icon = Image.open("cd_icon.png")
        self.cd_icon = self.cd_icon.resize((100, 100), Image.LANCZOS)  # Use LANCZOS for resizing
        self.cd_icon_tk = ImageTk.PhotoImage(self.cd_icon)

        self.speaker_icon = Image.open("speaker_icon.png")
        self.speaker_icon = self.speaker_icon.resize((100, 100), Image.LANCZOS)  # Use LANCZOS for resizing
        self.speaker_icon_tk = ImageTk.PhotoImage(self.speaker_icon)

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        # Frame for song controls
        song_frame = tk.Frame(self.master, bg='lightgray')
        song_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # CD Icon
        cd_label = tk.Label(song_frame, image=self.cd_icon_tk, bg='lightgray')
        cd_label.pack(pady=(20, 0))

        self.song_label = tk.Label(song_frame, text="Song Control", bg='lightgray', font=("Arial", 14))
        self.song_label.pack(pady=(10, 0))

        # Load song button
        self.load_button = tk.Button(song_frame, text="Load Song", command=self.load_song)
        self.load_button.pack(pady=5)

        # Play, Pause, Unpause, and Stop buttons for the song
        self.play_button = tk.Button(song_frame, text="Play Song", command=self.start_playing_song)
        self.play_button.pack(pady=5)

        self.pause_button = tk.Button(song_frame, text="Pause Song", command=self.pause_song)
        self.pause_button.pack(pady=5)

        self.unpause_button = tk.Button(song_frame, text="Unpause Song", command=self.unpause_song)
        self.unpause_button.pack(pady=5)

        self.stop_button = tk.Button(song_frame, text="Stop Song", command=self.stop_song)
        self.stop_button.pack(pady=5)

        # Seek Bar
        self.seek_bar = tk.Scale(song_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.seek_song)
        self.seek_bar.pack(pady=10)

        # BassOTron Label
        self.bassotron_label = tk.Label(self.master, text="BassOTron", bg='lightgray', font=("Arial", 24, "bold"))
        self.bassotron_label.pack(pady=(20, 0))

        # Frame for bass controls
        bass_frame = tk.Frame(self.master, bg='lightgray')
        bass_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        # Speaker Icon
        speaker_label = tk.Label(bass_frame, image=self.speaker_icon_tk, bg='lightgray')
        speaker_label.pack(pady=(20, 0))

        self.bass_label = tk.Label(bass_frame, text="Bass Control", bg='lightgray', font=("Arial", 14))
        self.bass_label.pack(pady=(10, 0))

        # Bass Frequency Controls
        self.bass_freq_label = tk.Label(bass_frame, text="Bass Frequency (Hz)", bg='lightgray')
        self.bass_freq_label.pack()

        self.bass_freq_scale = tk.Scale(bass_frame, from_=20, to=200, orient=tk.HORIZONTAL)
        self.bass_freq_scale.set(100)  # Default frequency
        self.bass_freq_scale.pack()

        # Play and Stop buttons for Bass
        self.play_bass_button = tk.Button(bass_frame, text="Play Bass", command=self.start_playing_bass)
        self.play_bass_button.pack(pady=5)

        self.stop_bass_button = tk.Button(bass_frame, text="Stop Bass", command=self.stop_bass)
        self.stop_bass_button.pack(pady=5)

        # Update the seek bar while the song is playing
        self.update_seek_bar()

    def load_song(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3")])
        if self.file_path:
            pygame.mixer.music.load(self.file_path)
            self.seek_bar.config(to=int(pygame.mixer.Sound(self.file_path).get_length()))

    def start_playing_song(self):
        pygame.mixer.music.play()
        self.is_song_playing = True
        self.update_seek_bar()  # Start updating the seek bar

    def pause_song(self):
        if self.is_song_playing:
            pygame.mixer.music.pause()
            self.is_song_playing = False

    def unpause_song(self):
        if not self.is_song_playing:
            pygame.mixer.music.unpause()
            self.is_song_playing = True

    def stop_song(self):
        pygame.mixer.music.stop()
        self.is_song_playing = False
        self.seek_bar.set(0)  # Reset seek bar

    def seek_song(self, value):
        if self.is_song_playing:
            # Convert the seek bar value to seconds
            new_position = float(value) / 100 * pygame.mixer.Sound(self.file_path).get_length()
            pygame.mixer.music.set_pos(new_position)

    def start_playing_bass(self):
        self.current_frequency = self.bass_freq_scale.get()
        self.is_bass_playing = True
        self.generate_bass_tone()

    def stop_bass(self):
        if self.current_sound:
            self.current_sound.stop()
            self.is_bass_playing = False

    def generate_bass_tone(self):
        if self.is_bass_playing:
            sample_rate = 44100
            duration = 1.0  # Duration of the sound in seconds
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            audio_data = 0.5 * np.sin(2 * np.pi * self.current_frequency * t)
            audio_data = np.int16(audio_data * 32767)

            # Convert to a 2D array for stereo sound
            audio_data = np.array([audio_data, audio_data]).T
            
            # Ensure the array is contiguous
            audio_data = np.ascontiguousarray(audio_data)

            self.current_sound = pygame.sndarray.make_sound(audio_data)
            self.current_sound.play(-1)  # Loop the bass sound

    def update_seek_bar(self):
        if self.is_song_playing:
            current_position = pygame.mixer.music.get_pos() / 1000  # Get current position in seconds
            song_length = pygame.mixer.Sound(self.file_path).get_length()
            if song_length > 0:
                self.seek_bar.set(current_position / song_length * 100)
            self.master.after(1000, self.update_seek_bar)  # Update every second

if __name__ == "__main__":
    root = tk.Tk()
    app = BassOTronApp(root)
    root.mainloop()
