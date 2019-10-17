import os
import platform
import logging
import queue
import threading
import hashlib

import skills.commands as cm
from skills.sentences import Lang
from pydub import AudioSegment
from pydub.playback import play
from google.cloud import texttospeech
from definitions import VOICE_OUTPUT_FILES_DIR
from pathlib import Path


class TextToSpeech:

    def __init__(self, speak_finished_event: threading.Event()):
        self.speak_finished_event = speak_finished_event

        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.__run)
        self.thread.daemon = True
        self.thread.start()

    def speech_text(self, text_to_speech: str, lang: Lang):
        self.speak_finished_event.clear()
        self.queue.put(
            cm.SpeechCommand(
                self.__speech_text,
                text_to_speech,
                lang
            )
        )

    def __run(self):
        while True:
            command = self.queue.get()  # type: cm.SpeechCommand
            command.method(command)

    def __play_mp3_file(self, filename: str):
        if platform.system() == 'Darwin':
            sound = AudioSegment.from_file(filename, format="mp3")
            play(sound)
        else:
            os.system('mpg123 -q ' + filename)

    @staticmethod
    def __get_mp3_file_name(command: cm.SpeechCommand):
        text = command.text_to_speech + command.language.value
        return hashlib.md5(text.encode('utf-8')).hexdigest() + '.mp3'

    def __speech_text(self, command: cm.SpeechCommand):
        file_name = os.path.join(VOICE_OUTPUT_FILES_DIR, self.__get_mp3_file_name(command))
        if not (Path(file_name)).is_file():
            self.__synthesize_text(command, file_name)

        self.__play_mp3_file(file_name)
        self.speak_finished_event.set()

    @staticmethod
    def __synthesize_text(command: cm.SpeechCommand, file_name: str):
        client = texttospeech.TextToSpeechClient()

        input_text = texttospeech.types.SynthesisInput(text=command.text_to_speech)

        voice = texttospeech.types.VoiceSelectionParams(
            language_code=command.language.value,
            ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE,
            name="pl-PL-Standard-E"
        )

        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)

        response = client.synthesize_speech(input_text, voice, audio_config)

        # The response's audio_content is binary.
        with open(file_name, 'wb') as out:
            out.write(response.audio_content)
            logging.debug('Audio content written to file "%s"', file_name)
