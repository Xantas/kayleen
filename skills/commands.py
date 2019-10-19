from skills.sentences import Lang
from threading import Event


class BaseCommand:
    def __init__(self, blocking_event: Event, is_blocking: bool):
        self.is_blocking = is_blocking
        self.blocking_event = blocking_event


class LanguageCommand(BaseCommand):
    def __init__(self, language: Lang, blocking_event: Event, is_blocking: bool):
        super().__init__(blocking_event, is_blocking)
        self.language = language


class CallMethodCommand(LanguageCommand):
    def __init__(self, method: (), language: Lang, blocking_event: Event, is_blocking: bool):
        super().__init__(language, blocking_event, is_blocking)
        self.method = method


class SpeechCommand(LanguageCommand):
    def __init__(self, text_to_speech: str, language: Lang, blocking_event: Event, is_blocking: bool):
        super().__init__(language, blocking_event, is_blocking)
        self.text_to_speech = text_to_speech


class VoiceRecognizedCommand(BaseCommand):
    def __init__(self, recognized_text: str, blocking_event: Event, is_blocking: bool):
        super().__init__(blocking_event, is_blocking)
        self.recognized_text = recognized_text


class CommandFactory:
    def __init__(self, language: Lang):
        self.language = language

    def create_call_method_command(self, method: ()):
        return CallMethodCommand(method, self.language, Event(), False)

    def create_call_method_blocking_command(self, method: ()):
        return CallMethodCommand(method, self.language, Event(), True)

    def create_speech_command(self, text_to_speech: str):
        return SpeechCommand(text_to_speech, self.language, Event(), True)

    @staticmethod
    def create_voice_recognized_command(recognized_text: str):
        return VoiceRecognizedCommand(recognized_text, Event(), False)

    @staticmethod
    def create_voice_recognized_blocked_command(recognized_text: str):
        return VoiceRecognizedCommand(recognized_text, Event(), True)
