import enum
from skills.voices import AvailableVoices


class SentenceKey(enum.Enum):
    hello = 1
    im_listening = 2
    what_i_recognized = 3
    shut_down = 4
    unknown_command = 5
    empty_command = 6
    wake_me_up = 7
    confirm = 8
    unconfirmed = 9
    list_voices = 10
    unrecognized_voice_model = 11
    present_voice = 12


class Lang(enum.Enum):
    def __str__(self):
        return str(self.value)

    PL = 'pl-PL'
    EN = 'en-EN'


pl_female = {
    SentenceKey.hello: 'Cześć, jestem Kayleen',
    SentenceKey.im_listening: 'Oczekuję komendy głosowej',
    SentenceKey.what_i_recognized: 'A oto, co zrozumiałam:',
    SentenceKey.shut_down: 'Buziaczki. Będę tęskniła.',
    SentenceKey.unknown_command: 'Niestety. Nie rozpoznaję tego polecenia. Smuteczek!',
    SentenceKey.empty_command: 'Niestety nic nie powiedziałeś. Masz problemy z mówieniem?',
    SentenceKey.wake_me_up: 'Jeżeli chcesz, abym słuchała co do mnie mówisz zawołaj mnie po imieniu',
    SentenceKey.confirm: 'Jeżeli potwierdzasz komendę powiedz - TAK',
    SentenceKey.unconfirmed: 'Komenda nie została potwierdzona. Pomijam.',
    SentenceKey.list_voices: 'Wybierz głos podając numer. Dostępne są: ',
    SentenceKey.unrecognized_voice_model: 'No takim głosem to ja nie potrafię mówić',
    SentenceKey.present_voice: 'To teraz porozmawiamy sobie inaczej',
}

pl_male = {
    SentenceKey.hello: 'Cześć, jestem Sam',
    SentenceKey.im_listening: 'Oczekuję komendy głosowej',
    SentenceKey.what_i_recognized: 'A oto, co zrozumiałem:',
    SentenceKey.shut_down: 'Fajnie się gadało. Przechodzę w niebyt. Do usłyszenia',
    SentenceKey.unknown_command: 'Przykro mi, ale niestety nie rozpoznaję tego polecenia.',
    SentenceKey.empty_command: 'Niestety nic nie powiedziałeś. Masz problemy z artykulacją?',
    SentenceKey.wake_me_up: 'Jeżeli chcesz, abym słuchał co do mnie mówisz wciśnij przycisk',
    SentenceKey.confirm: 'Jeżeli potwierdzasz komendę powiedz - TAK',
    SentenceKey.unconfirmed: 'Komenda nie została potwierdzona. Pomijam.',
    SentenceKey.list_voices: 'Wybierz głos podając numer. Dostępne są: ',
    SentenceKey.unrecognized_voice_model: 'Takim głosem to ja nie potrafię mówić',
    SentenceKey.present_voice: 'Cieszę się, że wolisz pogadać po męsku',
}

en = {
    SentenceKey.hello: 'Hello, my name is Kayleen',
    SentenceKey.im_listening: 'I expect a voice command',
    SentenceKey.what_i_recognized: 'Here is what I understood:',
    SentenceKey.shut_down: 'Bye',
    SentenceKey.unknown_command: 'Unknown command',
    SentenceKey.empty_command: 'Empty command',
    SentenceKey.wake_me_up: 'Push the button if you need my attention',
    SentenceKey.confirm: 'Say YES to confirm',
    SentenceKey.unconfirmed: 'Unconfirmed command - skipping!',
    SentenceKey.list_voices: 'Choice voice: ',
    SentenceKey.unrecognized_voice_model: 'Unrecognized voice',
}


def get_sentence(key: SentenceKey, lang: Lang, voice: AvailableVoices) -> str:
    if lang is Lang.EN:
        dictionary = en
    elif lang is Lang.PL and voice is AvailableVoices.kayleen:
        dictionary = pl_female
    elif lang is Lang.PL and voice is AvailableVoices.sam:
        dictionary = pl_male
    else:
        dictionary = pl_female

    if key in dictionary:
        return dictionary[key]
    else:
        return 'undefined sentence'
