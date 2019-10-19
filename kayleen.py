import sys
import enum
import queue
import threading
import time
import logging
import signal
from skills.commands import CommandFactory
import skills.commands as cm
import skills.sentences as txt
from skills.text_to_speech import TextToSpeech
from skills.speech_to_text import VoiceCommandRecognizer
from skills.blinker import Blinker


class KayleenStatus(enum.Enum):
    sleeping = 0
    working = 1
    initialising = 2
    killed = 3


class Kayleen:
    def __init__(self, develop_mode: bool) -> None:

        signal.signal(signal.SIGINT, self.__shut_down)
        signal.signal(signal.SIGTERM, self.__shut_down)

        self.develop_mode = develop_mode
        self.status = KayleenStatus.sleeping

        self.language = cm.Lang.PL
        self.cmFactory = CommandFactory(self.language)

        self.async_command_queue = queue.Queue()

        self.text_to_speech_processor = TextToSpeech(
            develop_mode
        )
        self.voice_commands_recognizer = VoiceCommandRecognizer(
            self.async_command_queue,
            develop_mode
        )
        self.blinker = Blinker()

        self.thread = threading.Thread(target=self.__run)
        self.thread.daemon = True
        self.thread.start()

    def __exit_gracefully(self, signum, frame):
        self.kill_now = True

    def wake_up(self):
        logging.info("Zaczynam się budzić ...")
        self.status = KayleenStatus.initialising
        self.blinker.wakeup()
        self.__sync_say(txt.get_sentence(txt.SentenceKey.hello))
        self.status = KayleenStatus.working
        self.async_command_queue.put(
            self.cmFactory.create_call_method_command(self.__listen_to_my_voice)
        )

    def shut_down(self):
        self.async_command_queue.put(
            self.cmFactory.create_call_method_command(self.__shut_down)
        )

    def is_sleeping(self):
        return self.status is KayleenStatus.sleeping

    def want_to_kill(self):
        return self.status is KayleenStatus.killed

    def heart_beat(self):
        pass

    def __run(self):
        while True:
            command = self.async_command_queue.get()
            if command.is_blocking:
                command.blocking_event.clear()

            if isinstance(command, cm.VoiceRecognizedCommand):
                self.__process_voice_command(command)
            else:
                command.method(command)

            if command.is_blocking:
                command.blocking_event.wait()

    def __shut_down(self, signum, frame):
        logging.info("Znikam, pa ...")
        self.__sync_say(txt.get_sentence(txt.SentenceKey.shut_down))
        time.sleep(4)
        self.status = KayleenStatus.killed

    def __go_to_sleep(self, command: cm.CallMethodCommand):
        logging.info("Rozpoczynam usypianie Kaylen")
        self.status = KayleenStatus.sleeping

    def __sync_say(self, text_to_speak: str):
        self.blinker.listen()
        command = self.cmFactory.create_speech_command(text_to_speak)
        self.text_to_speech_processor.speech_text(command)
        command.blocking_event.wait()
        self.blinker.off()

    def __listen_to_my_voice(self, command: cm.CallMethodCommand):
        self.__sync_say(txt.get_sentence(txt.SentenceKey.im_listening))

        self.blinker.speak()
        self.voice_commands_recognizer.listen_me(self.language)
        self.blinker.off()

    def __process_voice_command(self, command: cm.VoiceRecognizedCommand):
        logging.info("przetwarzam: " + command.recognized_text)
        self.__sync_say(txt.get_sentence(txt.SentenceKey.what_i_recognized))
        self.__sync_say(command.recognized_text)

        self.__sync_say(txt.get_sentence(txt.SentenceKey.unknown_command))


def main():
    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    # logging.getLogger().setLevel(logging.DEBUG)

    develop_mode = False

    for arg in sys.argv:
        if arg == '--dev':
            develop_mode = True

    kayleen = Kayleen(develop_mode)
    kayleen.wake_up()

    while True:
        time.sleep(0.5)
        if kayleen.status is KayleenStatus.killed:
            break


if __name__ == '__main__':
    main()
