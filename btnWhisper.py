import queue
import numpy  # Make sure NumPy is loaded before it is used in the callback
import keyboard
import sys
import soundfile as sf
import sounddevice as sd
import tempfile
import threading
import os


class BtnWhisper:
    def __init__(self, args, client):
        self.is_recording = False
        self.is_running = False
        self.q = queue.Queue()
        self.args = args
        self.sd_input_stream = None
        self.sound_file = None
        self.thread = None
        self.client = client
        self.filename = None

    def process_data(self):
        while self.is_running:
            if self.is_recording and self.sound_file and not self.q.empty():
                self.sound_file.write(self.q.get())
    
    def get_transcriptions(self, audio_file):
        print("Transcribing...")
        audio_file = open(audio_file, "rb")
        translation = self.client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        print(translation.text)
        return translation.text

    def create_random_filename(self):
        with tempfile.NamedTemporaryFile(prefix="delme_rec_unlimited_", suffix=".wav", delete=True) as temp_file:
            temp_filename = temp_file.name
        return temp_filename

    def start_recording(self):
        if self.is_recording:
            print("Already recording...")
        else:
            self.filename = self.create_random_filename()
            self.is_recording = True
            self.is_running = True
            self.sound_file = sf.SoundFile(
                self.filename,
                mode="x",
                samplerate=self.args.samplerate,
                channels=self.args.channels,
                subtype=self.args.subtype,
            )
            self.sd_input_stream = sd.InputStream(
                samplerate=self.args.samplerate,
                device=self.args.device,
                channels=self.args.channels,
                callback=self.callback,
                blocksize=8192,  # Use a bigger blocksize to reduce CPU load
            )
            self.sd_input_stream.start()
            self.thread = threading.Thread(target=self.process_data)
            self.thread.start()
            print("Start recording...")

    def end_recording(self):
        if not self.is_recording:
            print("Not recording...")
        else:
            self.is_recording = False

            # End thread
            self.is_running = False
            self.thread.join()
            self.thread = None
            while not self.q.empty():
                self.sound_file.write(self.q.get())

            self.sound_file.close()
            self.sound_file = None
            self.sd_input_stream.stop()
            self.sd_input_stream = None
            self.get_transcriptions(self.filename)
            print("End recording...")

    def add_listener(self):
        keyboard.add_hotkey("ctrl+alt+j", self.start_recording)
        keyboard.add_hotkey("ctrl+alt+m", self.end_recording)

    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

