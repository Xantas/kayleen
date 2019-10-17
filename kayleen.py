import enum
import queue
import threading
import time
import logging
import signal
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
    def __init__(self) -> None:
        signal.signal(signal.SIGINT, self.__shut_down)
        signal.signal(signal.SIGTERM, self.__shut_down)

        self.status = KayleenStatus.sleeping

        self.language = cm.Lang.PL

        self.command_queue = queue.Queue()

        self.next = threading.Event()
        self.speak_finished_event = threading.Event()
        self.listen_finished_event = threading.Event()

        self.text_to_speech_processor = TextToSpeech(self.speak_finished_event)
        self.voice_commands_recognizer = VoiceCommandRecognizer(
            self.command_queue, self.listen_finished_event
        )
        self.blinker = Blinker()

        self.thread = threading.Thread(target=self.__run)
        self.thread.daemon = True
        self.thread.start()

    def __exit_gracefully(self, signum, frame):
        self.kill_now = True

    def wake_up(self):
        self.command_queue.put(cm.Command(self.__wake_up))
        self.command_queue.put(
            cm.SpeechCommand(
                self.__say,
                txt.get_sentence(txt.SentenceKey.hello),
                self.language
            )
        )
        self.blinker.listen()
        self.speak_finished_event.clear()
        self.speak_finished_event.wait()
        self.command_queue.put(
            cm.SpeechCommand(
                self.__say,
                txt.get_sentence(txt.SentenceKey.im_listening),
                self.language
            )
        )
        self.speak_finished_event.clear()
        self.speak_finished_event.wait()
        self.blinker.off()
        self.command_queue.put(cm.Command(self.__listen_to_my_voice))

    def shut_down(self):
        self.command_queue.put(cm.Command(self.__shut_down))

    def is_sleeping(self):
        return self.status is KayleenStatus.sleeping

    def want_to_kill(self):
        return self.status is KayleenStatus.killed

    def heart_beat(self):
        pass

    def __run(self):
        while True:
            command = self.command_queue.get()
            if isinstance(command, cm.VoiceRecognizedCommand):
                self.__process_voice_command(command)
            else:
                command.method(command)

    def __shut_down(self, signum, frame):
        logging.info("Znikam, pa ...")
        self.command_queue.put(
            cm.SpeechCommand(
                self.__say,
                txt.get_sentence(txt.SentenceKey.shut_down),
                self.language
            )
        )
        self.blinker.off()
        time.sleep(4)
        self.status = KayleenStatus.killed

    def __wake_up(self, command: cm.Command):
        logging.info("Zaczynam się budzić ...")
        self.status = KayleenStatus.initialising
        self.blinker.wakeup()
        time.sleep(2)
        self.status = KayleenStatus.working

    def __go_to_sleep(self, command: cm.Command):
        logging.info("Rozpoczynam usypianie Kaylen")
        self.status = KayleenStatus.sleeping

    def __say(self, command: cm.SpeechCommand):
        self.text_to_speech_processor.speech_text(command.text_to_speech, command.language)

    def __listen_to_my_voice(self, command: cm.Command):
        self.blinker.speak()
        self.listen_finished_event.clear()
        self.voice_commands_recognizer.listen_me()
        self.listen_finished_event.wait()
        self.blinker.off()

    def __process_voice_command(self, command: cm.VoiceRecognizedCommand):
        logging.info("przetwarzam: " + command.recognized_text)
        self.blinker.listen()
        self.command_queue.put(
            cm.SpeechCommand(
                self.__say,
                txt.get_sentence(txt.SentenceKey.what_im_recognized),
                self.language
            )
        )
        self.blinker.listen()
        self.speak_finished_event.wait()
        self.command_queue.put(
            cm.SpeechCommand(
                self.__say,
                command.recognized_text,
                self.language
            )
        )
        self.blinker.listen()
        self.speak_finished_event.wait()
        self.command_queue.put(
            cm.SpeechCommand(
                self.__say,
                txt.get_sentence(txt.SentenceKey.unknown_command),

                self.language
            )
        )



def main():
    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    logging.getLogger().setLevel(logging.DEBUG)
    kayleen = Kayleen()
    kayleen.wake_up()

    while True:
        time.sleep(0.5)
        if kayleen.status is KayleenStatus.killed:
            break


if __name__ == '__main__':
    main()
