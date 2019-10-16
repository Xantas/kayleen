import enum

from skills.commands.command import Command


class SpeechCommandTypes(enum.Enum):
    standard = 'standard'
    empty = 'empty'


class SpeechCommand:
    def __init__(self, text_to_speech):
        super().__init__()
        self.text_to_speech = text_to_speech
