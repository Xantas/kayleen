import enum


class AvailableVoices(enum.Enum):
    def __str__(self):
        return str(self.value)

    kayleen = 1
    sam = 2

    @staticmethod
    def list():
        return [e.value for e in AvailableVoices]


available_voices = {
    AvailableVoices.sam: 'pl-PL-Standard-B',
    AvailableVoices.kayleen: 'pl-PL-Standard-E',
}