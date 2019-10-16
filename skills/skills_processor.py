import concurrent.futures
import enum
import logging
import queue
import threading
import time

from skills.commands.speech_commands import SpeechCommand
from skills.texttospeech.processor import process_speech_commands


class SkillsStatus(enum.Enum):
    offline = 0
    online = 1
    initialising = 2
    disabling = 3


class SkillsProcessor:

    def __init__(self):

        self._status = SkillsStatus.offline
        self._toSpeechQueue = queue.PriorityQueue()

        self.speech_stop_event = threading.Event()

    def shut_down(self):
        self._status = SkillsStatus.disabling
        time.sleep(2)
        self._status = SkillsStatus.offline

    def start_up(self):
        self._status = SkillsStatus.initialising
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(process_speech_commands, self._toSpeechQueue, self.speech_stop_event)

            time.sleep(0.1)
            logging.info("Main: about to set event")

        self._status = SkillsStatus.online
        self._toSpeechQueue.put(SpeechCommand("test"))

    def offline(self):
        return self._status is SkillsStatus.offline

    def online(self):
        return self._status is SkillsStatus.online
