import queue
from skills.commands import CommandFactory
from skills.commands import SystemCommandsDefinition
from skills.commands import Lang


class Reactor:
    confirmation_sentences = ('tak', 'ok', 'yes', 'confirm', 'potwierdzam')

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
        test = recognized_text in self.confirmation_sentences
        return test

    def __exit_cmd(self):
        self.command_bus.put(
            CommandFactory.create_exit_cmd()
        )

    def __exit_cmd(self):
        self.command_bus.put(CommandFactory.create_exit_cmd())

    def __confirm_cmd(self):
        pass
        # self.command_bus.put(
        #     CommandFactory.create_speech_command(SentenceKey.hello, self.language))

        #self.command_bus.put(CommandFactory.create_defined_command(SystemCommandsDefinition.confirm))

