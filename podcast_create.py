###
# curl --location 'https://ttsmp3.com/makemp3_new.php' \
#  --header 'Content-Type: application/x-www-form-urlencoded' \
# --data-urlencode 'msg=Писать истории' \
# --data-urlencode 'lang=Tatyana' \
# --data-urlencode 'source=ttsmp3'


# curl --location 'https://ttsmp3.com/makemp3_new.php' \
# --header 'Content-Type: application/x-www-form-urlencoded' \
# --data-urlencode 'msg=der Anfang der Erzählung, der Vorlesung war ziemlich unklar' \
# --data-urlencode 'lang=Hans' \
# --data-urlencode 'source=ttsmp3'


def createmp3(text):
    print(text)


import tomllib
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Konjugation:
    pres: str
    prat: str
    perfekt: str

@dataclass
class Example:
    ru: str
    de: str

@dataclass
class Word:
    ru: str
    de: str
    syn: Optional[str] = None
    kon: Optional[Konjugation] = None
    ex: list[Example] = field(default_factory=list)

    @staticmethod
    def from_dict(word: dict[str, Any]) -> 'Word':
        return Word(
            ru=word['ru'],
            de=word['de'],
            syn=word['syn'] if 'syn' in word else None,
            kon=Konjugation(**word['kon']) if 'kon' in word else None,
            ex=list([ Example(**ex) for ex in word['ex']]) if 'ex' in word else [],
        )

def load(file: str) -> list[Word]:
    with open(file, "rb") as toml:
        #todo validate toml
        data = tomllib.load(toml) 
    return list([Word.from_dict(word) for word in data['word']])

data = load("topics/001.toml")


for word in data:
    createmp3(word.ru)
    createmp3(word.de)
    if word.syn: 
        createmp3(word.syn)
    if word.kon: 
        createmp3(": " + word.kon.pres + ", : " + word.kon.prat + ", : " + word.kon.perfekt )
    for example in word.ex:
        createmp3("   " + example.ru )
        createmp3("   " + example.de )



