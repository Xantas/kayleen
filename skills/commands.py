import enum
from skills.sentences import Lang
from threading import Event


class SystemCommandsDefinition(enum.Enum):
    exit = 0
    confirm = 1
    say = 2
    listen = 3
    empty_voice_cmd = 4
    recognized_voice_cmd = 5
    unrecognized_voice_cmd = 6
    change_voice = 7


class CommandConfirmationStatus(enum.Enum):
    no_confirmation_needed = -1
    unprocessed = 0
    confirmed = 1
    declined = 2


class BaseCommand:
    def __init__(
            self,
            blocking_event: Event,
            is_blocking: bool,
            confirmation_status: CommandConfirmationStatus = CommandConfirmationStatus.no_confirmation_needed
    ):
        self.confirmation_status = confirmation_status
        self.is_blocking = is_blocking
        self.blocking_event = blocking_event

    def confirm(self):
        self.confirmation_status = CommandConfirmationStatus.confirmed

    def decline(self):
        self.confirmation_status = CommandConfirmationStatus.declined


class CommandBusCommand(BaseCommand):
    def __init__(
            self,
            command_type: SystemCommandsDefinition,
            blocking_event: Event,
            is_blocking: bool,
            payload: object = None,
            confirmation_status: CommandConfirmationStatus = CommandConfirmationStatus.no_confirmation_needed
    ):
        super().__init__(blocking_event, is_blocking, confirmation_status)
        self.payload = payload
        self.command_type = command_type


class SpeechCommand(BaseCommand):
    def __init__(self, text_to_speech: str, language: Lang, blocking_event: Event, is_blocking: bool):
        super().__init__(blocking_event, is_blocking)
        self.language = language
        self.text_to_speech = text_to_speech


class CommandFactory:
    @staticmethod
    def create_change_voice_cmd():
        return CommandBusCommand(
            command_type=SystemCommandsDefinition.change_voice,
            blocking_event=Event(),
            is_blocking=True
        )

    @staticmethod
    def create_exit_cmd():
        return CommandBusCommand(
            command_type=SystemCommandsDefinition.exit,
            blocking_event=Event(),
            is_blocking=True,
            confirmation_status=CommandConfirmationStatus.unprocessed
        )

    @staticmethod
    def create_listen_to_my_voice_cmd():
        return CommandBusCommand(
            command_type=SystemCommandsDefinition.listen,
            blocking_event=Event(),
            is_blocking=True
        )

    @staticmethod
    def create_empty_voice_cmd():
        return CommandBusCommand(
            command_type=SystemCommandsDefinition.empty_voice_cmd,
            blocking_event=Event(),
            is_blocking=False
        )

    @staticmethod
    def create_voice_recognized_cmd(payload: object):
        return CommandBusCommand(
            command_type=SystemCommandsDefinition.recognized_voice_cmd,
            blocking_event=Event(),
            is_blocking=False,
            payload=payload
        )

    @staticmethod
    def create_unrecognized_voice_cmd():
        return CommandBusCommand(
            command_type=SystemCommandsDefinition.unrecognized_voice_cmd,
            blocking_event=Event(),
            is_blocking=False
        )

    @staticmethod
    def create_speech_cmd(text_to_speech: str, language: Lang):
        return SpeechCommand(
            text_to_speech=text_to_speech,
            language=language,
            blocking_event=Event(),
            is_blocking=True
        )
