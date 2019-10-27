import sys
import enum
import queue
import threading
import time
import logging
import signal
import platform
from skills.commands import CommandBusCommand
from skills.commands import CommandFactory
from skills.commands import SystemCommandsDefinition
from skills.commands import CommandConfirmationStatus
from skills.hotword_detector import SnowboyDecoder
from skills.player import Player
from skills.sentences import SentenceKey
import skills.commands as cm
import skills.sentences as txt
from skills.text_to_speech import TextToSpeech
from skills.speech_to_text import VoiceCommandRecognizer
from skills.speech_to_text import VoiceCommandPayload
from skills.blinker import Blinker
from skills.speech_command_processor import Reactor
from skills.voices import AvailableVoices

try:
    import RPi.GPIO as GPIO
except ImportError:
    from device import rpi_mock as GPIO


class KayleenStatus(enum.Enum):
    sleeping = 0
    working = 1
    initialising = 2
    killed = 3


BUTTON = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)


class Kayleen:
    def __init__(self, develop_mode: bool) -> None:

        signal.signal(signal.SIGINT, self.__shut_down)
        signal.signal(signal.SIGTERM, self.__shut_down)

        self.develop_mode = develop_mode
        self.status = KayleenStatus.sleeping

        self.language = cm.Lang.PL

        self.async_command_bus = queue.Queue()

        self.text_to_speech_processor = TextToSpeech(
            develop_mode
        )
        self.voice_commands_recognizer = VoiceCommandRecognizer(
            self.async_command_bus,
            develop_mode
        )
        self.reactor = Reactor(
            self.async_command_bus,
            self.language,
            develop_mode
        )
        self.blinker = Blinker()
        self.detector = SnowboyDecoder(sensitivity=0.5)
        self.player = Player()

        self.thread = threading.Thread(target=self.__run)
        self.thread.daemon = True
        self.thread.start()

        self.__sync_say(SentenceKey.hello)
        self.__sync_say(SentenceKey.wake_me_up)

    def __run(self):
        while True:
            command = self.async_command_bus.get()
            if command.is_blocking:
                command.blocking_event.clear()

            self.__handle(command)

            if command.is_blocking:
                command.blocking_event.wait()

    def __exit_gracefully(self, signum, frame):
        self.__shut_down()

    def is_killed(self):
        return self.status is KayleenStatus.killed

    def start_snowboy(self):
        if not self.develop_mode:
            print('Listening... Press Ctrl+C to exit')
            self.detector.start(detected_callback=self.wake_up,
                                interrupt_check=self.is_killed,
                                sleep_time=0.03)
        else:
            input("Naciśnij enter aby zasymulowac budzenie ...")
            self.wake_up()

    def wake_up(self):
        # Player.play_ding_signal()
        logging.info("Zaczynam się budzić ...")
        if not self.develop_mode:
            self.detector.terminate()
        self.status = KayleenStatus.initialising
        self.blinker.wakeup()
        self.status = KayleenStatus.working
        self.async_command_bus.put(
            CommandFactory.create_listen_to_my_voice_cmd()
        )

    def __shut_down(self, signum=None, frame=None):
        logging.info("Przechodzę w niebyt ...")
        if not self.develop_mode:
            self.detector.terminate()
        while self.detector.is_running():
            print("czekam")
            time.sleep(0.05)
        self.__sync_say(SentenceKey.shut_down)
        time.sleep(2)
        self.status = KayleenStatus.killed

    def __go_to_sleep(self):
        logging.info("Usypiam")
        self.status = KayleenStatus.sleeping
        self.start_snowboy()

    def __sync_pure_text_say(self, text: str):
        self.blinker.listen()
        command = CommandFactory.create_speech_cmd(
            text,
            self.language
        )
        self.text_to_speech_processor.speech_text(command)
        command.blocking_event.wait()
        self.blinker.off()

    def __sync_say(self, sentence: SentenceKey):
        self.__sync_pure_text_say(txt.get_sentence(sentence, self.language, self.text_to_speech_processor.voice))

    def __listen_to_my_voice(self):
        self.__sync_say(SentenceKey.im_listening)
        self.blinker.speak()
        Player.play_dong_signal()
        self.voice_commands_recognizer.listen_me(self.language)
        self.blinker.off()

    def __syc_listen_to_my_voice(self):
        self.blinker.speak()
        Player.play_dong_signal()
        result = self.voice_commands_recognizer.sync_listen_me(self.language)
        self.blinker.off()
        return result

    def __process_empty_voice_command(self):
        self.__sync_say(SentenceKey.empty_command)
        self.__go_to_sleep()

    def __process_voice_command(self, payload: VoiceCommandPayload):
        logging.info("Przetwarzam: " + payload.recognized_text)
        self.blinker.think()
        self.__sync_say(SentenceKey.what_i_recognized)
        self.__sync_pure_text_say(payload.recognized_text)
        self.reactor.run_task_from_recognized_text(payload.recognized_text)

    def __unrecognized_voice_command(self):
        self.__sync_say(SentenceKey.unknown_command)
        self.__go_to_sleep()

    def __confirm_command(self, command: CommandBusCommand):
        self.__sync_say(SentenceKey.confirm)

        if self.reactor.is_confirmed(self.__syc_listen_to_my_voice()):
            command.confirm()
        else:
            command.decline()

        self.async_command_bus.put(command)

    def __change_voice_command(self):
        self.__sync_say(SentenceKey.list_voices)

        for voice in AvailableVoices:
            self.__sync_pure_text_say(voice.name)
            self.__sync_pure_text_say(str(voice.value))

        choice = self.reactor.choose_voice_from_text(
            self.__syc_listen_to_my_voice()
        )

        if choice is None:
            self.__sync_say(SentenceKey.unrecognized_voice_model)
        else:
            self.text_to_speech_processor.change_voice_to(choice)
            self.__sync_say(SentenceKey.present_voice)

        self.__go_to_sleep()

    def __play_music(self):
        logging.info("Odtwarzam muzykę")
        self.__sync_say(SentenceKey.playing_music)
        self.player.play_music()

        if platform.system() == 'Darwin':
            input("Wcisnij enter aby przerwać ...")
        else:
            while True:
                state = GPIO.input(BUTTON)
                if not state:
                    break
                time.sleep(0.05)

        self.player.stop_music()
        self.wake_up()

    def __handle(self, command: CommandBusCommand):
        if command.confirmation_status is CommandConfirmationStatus.unprocessed:
            self.__confirm_command(command)
            command.blocking_event.set()
            return
        elif command.confirmation_status is CommandConfirmationStatus.declined:
            self.__sync_say(SentenceKey.unconfirmed)
            command.blocking_event.set()
            self.__go_to_sleep()
            return

        if command.command_type is SystemCommandsDefinition.exit:
            self.__shut_down()
        elif command.command_type is SystemCommandsDefinition.listen:
            self.__listen_to_my_voice()
            command.blocking_event.set()
        elif command.command_type is SystemCommandsDefinition.empty_voice_cmd:
            self.__process_empty_voice_command()
        elif command.command_type is SystemCommandsDefinition.recognized_voice_cmd:
            self.__process_voice_command(command.payload)
        elif command.command_type is SystemCommandsDefinition.unrecognized_voice_cmd:
            self.__unrecognized_voice_command()
        elif command.command_type is SystemCommandsDefinition.confirm:
            self.__confirm_command(command.payload)
        elif command.command_type is SystemCommandsDefinition.change_voice:
            self.__change_voice_command()
            command.blocking_event.set()
        elif command.command_type is SystemCommandsDefinition.play_music:
            self.__play_music()
            command.blocking_event.set()


def main():
    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    # logging.getLogger().setLevel(logging.DEBUG)

    develop_mode = False

    for arg in sys.argv:
        if arg == '--dev':
            develop_mode = True

    kayleen = Kayleen(develop_mode)
    kayleen.start_snowboy()

    while True:
        if kayleen.is_killed():
            break
        time.sleep(2)


if __name__ == '__main__':
    main()
