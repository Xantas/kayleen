import pyaudio
import wave
import os
import platform
import time
import logging
import queue
import threading
import skills.commands as cm
import uuid
from skills.commands import VoiceRecognizedCommand
from definitions import VOICE_INPUT_FILES_DIR

SAMPLE_RATE = 16000
CHANNELS = 2
FRAME_WIDTH = 2
# run device/respeaker_device_idx.py to get index of device
RESPEAKER_DEVICE_INDEX = 2
CHUNK = 1024
RECORD_SECONDS = 5


class VoiceCommandRecognizer:
    def __init__(self, voice_command_queue: queue.Queue, listen_finished_event: threading.Event()):
        self.listen_finished_event = listen_finished_event
        self.voice_command_queue = voice_command_queue
        self.nextEventPresent = threading.Event()
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.__run)
        self.thread.daemon = True
        self.thread.start()

    def listen_me(self):
        logging.info('Słucham ...')
        self.listen_finished_event.clear()
        time.sleep(2)
        self.voice_command_queue.put(VoiceRecognizedCommand('moja super komenda'))
        self.listen_finished_event.set()

    def __run(self):
        while True:
            command = self.queue.get()  # type: cm.Command
            command.method(command)

    def __record_voice(self, command: cm.Command):
        if platform.system() == 'Darwin':
            print("MAC")
        else:
            self.__record_voice_raspi(command)

    def __record_voice_raspi(self, command: cm.Command) -> str:
        p = pyaudio.PyAudio()

        stream = p.open(
            rate=SAMPLE_RATE,
            format=p.get_format_from_width(FRAME_WIDTH),
            channels=CHANNELS,
            input=True,
            input_device_index=RESPEAKER_DEVICE_INDEX, )

        print("* recording")

        frames = []

        for i in range(0, int(SAMPLE_RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()

        file_name = os.path.join(VOICE_INPUT_FILES_DIR, str(uuid.uuid4()) + '.wav')

        wf = wave.open(file_name, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(p.get_format_from_width(FRAME_WIDTH)))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        return file_name
