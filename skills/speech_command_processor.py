import queue
from skills.commands import CommandFactory
from skills.commands import SystemCommandsDefinition
from skills.commands import Lang
from skills.voices import AvailableVoices


class Reactor:
    def __init__(
            self,
            command_bus: queue.Queue,
            language: Lang,
            develop_mode: bool
    ):
        self.language = language
        self.develop_mode = develop_mode
        self.command_bus = command_bus

        self.voice_commands_definitions = {
            'wyjdź': self.__exit_cmd,
            'zakończ': self.__exit_cmd,
            'głos': self.__change_voice_cmd,
            'graj': self.__play_music,
            'muzyka': self.__play_music,
            'muzykę': self.__play_music,
            'odtwarzaj': self.__play_music,
        }

    def run_task_from_recognized_text(self, recognized_text: str):
        for txt, cmd in self.voice_commands_definitions.items():
            if recognized_text.find(txt) >= 0:
                cmd()
                return
        self.command_bus.put(CommandFactory.create_unrecognized_voice_cmd())

    def run_confirmed_task(self, definition: SystemCommandsDefinition):
        self.command_bus.put(CommandFactory.create_unrecognized_voice_cmd())

    def is_confirmed(self, recognized_text: str):
        confirmation_sentences = ('tak', 'ok', 'yes', 'confirm', 'potwierdzam')
        test = recognized_text in confirmation_sentences
        return test

    def choose_voice_from_text(self, recognized_text: str):
        text_for_voices = {
            AvailableVoices.kayleen: (AvailableVoices.kayleen.name, '1', 'jeden', 'one', 'pierwszy', 'first'),
            AvailableVoices.sam: (AvailableVoices.sam.name, '2', 'dwa', 'two', 'drugi', 'second'),
        }

        for voice in AvailableVoices:
            if recognized_text in text_for_voices[voice]:
                return voice

        return None

    def __exit_cmd(self):
        self.command_bus.put(CommandFactory.create_exit_cmd())

    def __change_voice_cmd(self):
        self.command_bus.put(CommandFactory.create_change_voice_cmd())

    def __play_music(self):
        self.command_bus.put(CommandFactory.create_play_music_cmd())
