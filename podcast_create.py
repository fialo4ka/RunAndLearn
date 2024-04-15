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
from dataclasses import dataclass
from typing import Optional

@dataclass
class Word:
    ru: str
    de: str
    syn: Optional[str]

def load() -> list[Word]:
    with open("topics/001.toml", "rb") as toml:
        data = tomllib.load(toml)
    return list([Word(**word) for word in data['word']])

data = load()


for word in data['word']:
    createmp3(word['ru'])
    createmp3(word['de'])
    if 'syn' in word: 
        createmp3(word['syn'])
    if 'kon' in word: 
        createmp3(": " + word['kon']['pres'] + ", : " + word['kon']['prat'] + ", : " + word['kon']['perfekt'] )
    for example in word['ex']:
        createmp3("   " + example['ru'])
        createmp3("   " + example['de'])



