import logging
import queue
import threading

from google.cloud import texttospeech

from skills.commands.speech_commands import SpeechCommand

class TextToSpeech:

    def __init__(self):
        self.next = threading.Event()
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()


def __synthesize_text(text):
    """Synthesizes speech from the input string of text."""

    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.types.SynthesisInput(text=text)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='pl-PL',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    response = client.synthesize_speech(input_text, voice, audio_config)

    # The response's audio_content is binary.
    with open('output.mp3', 'wb') as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')


def process_speech_commands(speech_queue: queue.PriorityQueue, stop_event: threading.Event):
    logging.info("test")
    while not stop_event.is_set():
        message = speech_queue.get()  # type: SpeechCommand
        logging.info(
            "Consumer storing message: %s (size=%d)", message.text_to_speech, speech_queue.qsize()
        )
