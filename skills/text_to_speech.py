import os
import platform
import logging
import queue
import threading
import hashlib
from skills.commands import SpeechCommand
from pydub import AudioSegment
from pydub.playback import play
from google.cloud import texttospeech
from definitions import VOICE_OUTPUT_FILES_DIR
from pathlib import Path

from skills.voices import AvailableVoices, available_voices


class TextToSpeech:

    def __init__(self, develop_mode: bool):
        self.develop_mode = develop_mode

        self.voice = AvailableVoices.kayleen

        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.__run)
        self.thread.daemon = True
        self.thread.start()

    def change_voice_to(self, voice: AvailableVoices):
        self.voice = voice

    def speech_text(self, command: SpeechCommand):
        self.queue.put(command)

    def __run(self):
        while True:
            self.__speech_text(self.queue.get())

    def __speech_text(self, command: SpeechCommand):
        file_name = os.path.join(VOICE_OUTPUT_FILES_DIR, self.__get_mp3_file_name(command))
        if not (Path(file_name)).is_file():
            self.__synthesize_text(command, file_name)

        self.__play_mp3_file(file_name)
        command.blocking_event.set()

    def __play_mp3_file(self, filename: str):
        if platform.system() == 'Darwin':
            sound = AudioSegment.from_file(filename, format="mp3")
            play(sound)
        else:
            os.system('mpg123 -q ' + filename)

    def __get_mp3_file_name(self, command: SpeechCommand):
        text = ''.join([command.text_to_speech, command.language.value, str(self.voice.value)])
        return hashlib.sha1(text.encode('utf-8')).hexdigest() + '.mp3'

    def __synthesize_text(self, command: SpeechCommand, file_name: str):
        client = texttospeech.TextToSpeechClient()

        input_text = texttospeech.types.SynthesisInput(text=command.text_to_speech)

        voice = texttospeech.types.VoiceSelectionParams(
            language_code=command.language.value,
            ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE,
            name=available_voices[self.voice]
        )

        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)

        response = client.synthesize_speech(input_text, voice, audio_config)

        # The response's audio_content is binary.
        with open(file_name, 'wb') as out:
            out.write(response.audio_content)
            logging.debug('Audio content written to file "%s"', file_name)
