import queue
import numpy  # Make sure NumPy is loaded for SPEED UP before it is used in the callback
from dotenv import load_dotenv
from openai import OpenAI
import keyboard
import sys
import soundfile as sf
import sounddevice as sd
import tempfile
import threading
import os
from PyQt5.QtWidgets import QApplication


class BtnWhisper:
    def __init__(self):
        load_dotenv()
        self.is_recording = False
        self.q = queue.Queue()
        self.sound_file = None
        self.thread = None
        self.client = OpenAI()
        self.filename = None
        # Get samplerate of current device
        self.device = None
        device_info = sd.query_devices(self.device, "input")
        self.samplerate = int(device_info["default_samplerate"])
        self.channels = 1
        self.sd_input_stream = sd.InputStream(
            samplerate=self.samplerate,
            device=self.device,
            channels=self.channels,
            callback=self.callback,
            blocksize=8192,  # Use a bigger blocksize to reduce CPU load
        )
        self.recording_hotkey = "ctrl+alt+j"
        self.add_listener()

    def process_data(self):
        while self.is_recording:
            if self.sound_file and not self.q.empty():
                self.sound_file.write(self.q.get())
    
    def get_transcriptions(self, filename):
        print("Transcribing...")
        with open(filename, "rb") as f:
            transcription = self.client.audio.transcriptions.create(model="whisper-1", file=f)
        print(transcription.text)
        keyboard.write(transcription.text)
        return transcription.text

    def get_random_filename(self):
        with tempfile.NamedTemporaryFile(prefix="delme_rec_unlimited_", suffix=".wav", delete=True) as temp_file:
            temp_filename = temp_file.name
        return temp_filename

    def record(self):
        if not self.is_recording:
            self.filename = self.get_random_filename()
            self.is_recording = True
            self.sound_file = sf.SoundFile(
                self.filename,
                mode="x",
                samplerate=self.samplerate,
                channels=self.channels,
                subtype=None
            )
            self.thread = threading.Thread(target=self.process_data)
            self.sd_input_stream.start()
            self.thread.start()
            print("Start recording...")
        else:
            self.is_recording = False

            # End thread
            self.thread.join()
            self.thread = None
            while not self.q.empty():
                self.sound_file.write(self.q.get())
            self.sd_input_stream.stop()
            self.get_transcriptions(self.filename)
            self.delete_sound_file()
            print("End recording...")
        
    def delete_sound_file(self):
        if self.filename:
            self.is_recording = False
            if self.thread:
                self.thread.join()
            if self.sound_file:
                self.sound_file.close()
                self.sound_file = None
            os.remove(self.filename)
            self.filename = None
            print("Audio file has been deleted")

    def add_listener(self):
        keyboard.add_hotkey(self.recording_hotkey, self.record)
        # keyboard.add_hotkey("Esc", QApplication.instance().quit)
    
    def set_recording_hotkey(self, hotkey):
        self.recording_hotkey = hotkey
        self.add_listener()
        print("Hotkey has been set to: " + self.recording_hotkey)

    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

