import os
import platform
import wave
import pyaudio
from pygame import mixer
import time
from ctypes import *
from contextlib import contextmanager
from pydub import AudioSegment
from pydub.playback import play
from definitions import SOUND_FILES_DIR

SIGNAL_DING = os.path.join(SOUND_FILES_DIR, "ding.wav")
SIGNAL_DONG = os.path.join(SOUND_FILES_DIR, "dong.wav")
DEMO_SONG = os.path.join(SOUND_FILES_DIR, "now_we_are_free_cut.mp3")


def py_error_handler(filename, line, function, err, fmt):
    pass


ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)


@contextmanager
def no_alsa_error():
    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        pass


class Player:
    def __init__(self):
        self.mixer = mixer
        self.mixer.init()

    def play_music(self):
        self.mixer.music.load(DEMO_SONG)
        self.mixer.music.play()

    def stop_music(self):
        self.mixer.music.stop()

    @staticmethod
    def play_ding_signal():
        Player.play_wav_file(SIGNAL_DING)

    @staticmethod
    def play_dong_signal():
        Player.play_wav_file(SIGNAL_DONG)

    @staticmethod
    def play_mp3_file(filename: str):
        if platform.system() == 'Darwin':
            sound = AudioSegment.from_file(filename, format="mp3")
            play(sound)
        else:
            os.system('mpg123 -q ' + filename)

    @staticmethod
    def play_wav_file(file_name):
        wav_file = wave.open(file_name, 'rb')
        wav_file_data = wav_file.readframes(wav_file.getnframes())
        with no_alsa_error():
            audio = pyaudio.PyAudio()
        stream_out = audio.open(
            format=audio.get_format_from_width(wav_file.getsampwidth()),
            channels=wav_file.getnchannels(),
            rate=wav_file.getframerate(),
            input=False,
            output=True
        )
        stream_out.start_stream()
        stream_out.write(wav_file_data)
        time.sleep(0.2)
        stream_out.stop_stream()
        stream_out.close()
        audio.terminate()
