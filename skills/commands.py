from skills.sentences import Lang


class Command:
    def __init__(self, method: ()):
        self.method = method


class SpeechCommand(Command):
    def __init__(self, method: (), text_to_speech: str, language: Lang):
        super().__init__(method)
        self.language = language
        self.text_to_speech = text_to_speech


class VoiceRecognizedCommand:
    def __init__(self, recognized_text: str):
        self.recognized_text = recognized_text
