import enum


class SentenceKey(enum.Enum):
    hello = 1
    im_listening = 2
    what_im_recognized = 3
    shut_down = 4
    unknown_command = 5

class Lang(enum.Enum):
    def __str__(self):
        return str(self.value)
    PL = 'pl-PL'
    EN = 'en-EN'


pl = {
    SentenceKey.hello: 'Cześć, jestem Kayleen',
    SentenceKey.im_listening: 'Oczekuję komendy głosowej',
    SentenceKey.what_im_recognized: 'A oto, co zrozumiałam:',
    SentenceKey.shut_down: 'Będę tęskniła ...',
    SentenceKey.unknown_command: 'Niestety, nie rozpoznaję polecenia. Smuteczek!'
}

en = {
    SentenceKey.hello: 'Hello, my name is Kayleen',
    SentenceKey.im_listening: 'I expect a voice command',
    SentenceKey.what_im_recognized: 'Here is what I understood:',
    SentenceKey.shut_down: 'Bye',
    SentenceKey.unknown_command: 'Unknown command'
}


def get_sentence(key: SentenceKey, lang: Lang = Lang.PL) -> str:
    if lang is Lang.EN:
        dictionary = en
    else:
        dictionary = pl  # fallback na polski

    if key in dictionary:
        return dictionary[key]
    else:
        return 'undefined sentence'
