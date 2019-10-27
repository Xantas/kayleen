import signal
import os
import platform
import time
import logging
import queue
import uuid
import subprocess
from skills.commands import CommandFactory
from skills.sentences import Lang
from definitions import VOICE_INPUT_FILES_DIR
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
import io

SAMPLE_RATE = 16000
SAMPLE_FORMAT = 'S16_LE'
CHANNELS = 1
RECORD_SECONDS = 5


class GoogleVoiceRecognizer:
    def __init__(self, develop_mode: bool):
        self.develop_mode = develop_mode

    def sample_recognize(self, local_file_path, lang: Lang):
        """
        Transcribe a short audio file using synchronous speech recognition

        Args:
          local_file_path Path to local audio file, e.g. /path/audio.wav
        """

        client = speech_v1.SpeechClient()

        logging.debug("Próba rozpoznania mowy w pliku : %s", local_file_path)

        # The language of the supplied audio
        language_code = str(lang.value)

        # Sample rate in Hertz of the audio data sent
        sample_rate_hertz = SAMPLE_RATE

        # Encoding of audio data sent. This sample sets this explicitly.
        # This field is optional for FLAC and WAV audio formats.
        encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
        config = {
            "language_code": language_code,
            "sample_rate_hertz": sample_rate_hertz,
            "encoding": encoding,
        }
        with io.open(local_file_path, "rb") as f:
            content = f.read()
        audio = {"content": content}

        recognized_text = None

        response = client.recognize(config, audio)
        for result in response.results:
            # First alternative is the most probable result
            alternative = result.alternatives[0]
            logging.debug(u"Rozpoznany tekst: {}".format(alternative.transcript))
            recognized_text = alternative.transcript

        return recognized_text


class VoiceCommandPayload:
    def __init__(self, recognized_text: str):
        self.recognized_text = recognized_text


class VoiceCommandRecognizer:
    def __init__(
            self,
            command_bus: queue.Queue,
            develop_mode: bool
    ):
        self.develop_mode = develop_mode
        self.command_bus = command_bus

        self.googleRecognizer = GoogleVoiceRecognizer(develop_mode)

    def listen_me(self, language: Lang):
        logging.info('Słucham ...')

        if self.develop_mode:
            recognized_text = input('Wpisz tresc komendy ...')
        else:
            recognized_text = self.googleRecognizer.sample_recognize(
                self.__record_voice(),
                language
            )

        if recognized_text is None:
            command = CommandFactory.create_empty_voice_cmd()
        else:
            command = CommandFactory.create_voice_recognized_cmd(
                VoiceCommandPayload(recognized_text)
            )

        self.command_bus.put(
            command
        )

    def sync_listen_me(self, language: Lang):
        if self.develop_mode:
            return input("Wpisz tresc komendy synchronicznej ...")
        else:
            return self.googleRecognizer.sample_recognize(
                self.__record_voice(),
                language
            )

    def __record_voice(self) -> str:
        if self.develop_mode:
            return os.path.join(VOICE_INPUT_FILES_DIR, 'test_command.wav')
        else:
            if platform.system() == 'Darwin':
                return self.__record_voice_macos()
            else:
                return self.__record_voice_raspi()

    def __record_voice_macos(self) -> str:
        pass

    def __record_voice_raspi(self) -> str:
        file_name = os.path.join(VOICE_INPUT_FILES_DIR, str(uuid.uuid4()) + '.wav')
        args = ['arecord', '--quiet', '-d', str(RECORD_SECONDS), '-D', 'plughw:1', '-c{}'.format(CHANNELS), '-r',
                str(SAMPLE_RATE), '-f', SAMPLE_FORMAT, '-t', 'wav', '-V', 'mono', file_name]
        os.system(' '.join(args))
        logging.debug("Próbka głosowa nagrana")
        return file_name

    def __record_voice_raspi_subprocess(self) -> str:
        file_name = os.path.join(VOICE_INPUT_FILES_DIR, str(uuid.uuid4()) + '.wav')
        proc_args = ['arecord', '--quiet', '-D', 'plughw:1', '-c{}'.format(CHANNELS), '-r', str(SAMPLE_RATE),
                     '-f', SAMPLE_FORMAT, '-t', 'wav', '-V', 'mono', file_name]
        recording_process = subprocess.Popen(proc_args, shell=False, preexec_fn=os.setsid)
        time.sleep(RECORD_SECONDS)
        os.killpg(recording_process.pid, signal.SIGTERM)
        recording_process.terminate()
        recording_process = None
        print(" ")  # potrzebne do usuniecia blokad wierszy terminala przez arecord
        print(" ")
        logging.debug("Próbka głosowa nagrana")
        return file_name
