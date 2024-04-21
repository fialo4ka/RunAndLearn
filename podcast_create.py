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

def load(file: str):
    with open(file, "rb") as toml:
        #todo validate toml
        data = tomllib.load(toml) 
    return data

def getAuthor(file: str):
    return load(file)["author"]

def getWords(file: str) -> list[Word]:
    data = load(file)
    return list([Word.from_dict(word) for word in data['word']])




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


import requests
import json 

def postequest(dataText, language):
    url = "https://ttsmp3.com/makemp3_new.php"
    headers = {'Content-Type' : 'application/x-www-form-urlencoded'}
    if language == 0:
        data = {
            'msg' : dataText,
            'lang' : 'Vicki',
            'source' : 'ttsmp3'
        }
    else:
        data = {
            'msg' : dataText,
            'lang' : 'Tatyana',
            'source' : 'ttsmp3'
        }       

    response = requests.post(url, data, headers)
    
    print("Status Code", response.status_code)
    print("JSON Response ", response.json())
    return response.json()["URL"]

def getMp3(fileName, local_filename):
    local_filename = "temp/" + local_filename + ".mp3"
    with requests.get(fileName, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return local_filename


def downloadMp3(local_filename, text, language):
    fileName = postequest(text, language)
    getMp3(fileName, local_filename)

def ttsmp3Com(data):
    i = 0
    for word in data:
        downloadMp3(str(i) + "_ru", word.ru, 1)
        downloadMp3(str(i) + "_de", word.de, 0)
        if word.syn: 
            downloadMp3(str(i) + "_syn", word.syn, 0)
        if word.kon: 
            downloadMp3(str(i) + "_kon", ": " + word.kon.pres + ", : " + word.kon.prat + ", : " + word.kon.perfekt, 0)
        j = 0
        for example in word.ex:
            downloadMp3(str(i) + "_" + str(j) + "_x_ru", "   " + example.ru, 1)
            downloadMp3(str(i) + "_" + str(j) + "_x_de", "   " + example.de, 0)
            j = j +1
        i = i + 1

def concatunateFiles(files):
    return []


import lxml.etree as etree
from datetime import datetime

def updateRss(words, resultMp3, duration, title, author):
    xmlfilepath='podcast.xml' 
    tree = etree.parse(xmlfilepath)
    channel = tree.xpath('//rss/channel')[0]
    dateNow = datetime.now().strftime("%d/%m/%Y, %H:%M")
    date = tree.xpath('//rss/channel/lastBuildDate')
    date[0].text = dateNow
    itunes = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
    item = etree.SubElement(channel, 'Item')
    etree.SubElement(item, 'author').text = author  
    etree.SubElement(item, 'title').text = title
    etree.SubElement(item, 'description').text = ''    
    etree.SubElement(item, 'pubDate').text = dateNow   
    etree.SubElement(item, 'enclosure', url=resultMp3,type="audio/mpeg", length=""  ).text = ''  
    etree.SubElement(item, '{itunes}block').text = 'no'
    etree.SubElement(item, '{itunes}explicit').text = 'no'
    etree.SubElement(item, '{itunes}episodeType').text = 'full'
    etree.SubElement(item, '{itunes}title').text = title
    etree.SubElement(item, '{itunes}author').text = author 
    etree.SubElement(item, '{itunes}duration').text = duration
    item.insert(1, item[-1])
    with open(xmlfilepath, 'wb') as filetowrite:
        filetowrite.write('<?xml version=\"1.0\" encoding=\"UTF-8\"?>'.encode() +    etree.tostring(tree, pretty_print=True)     ) #e
        filetowrite.close()

def getTitle(fileName: str):
    list = fileName.split('/')
    return list[len(list)-1].replace('.toml', '')

def getDuration(resultMp3):
    return "12"


#load toml
url = "topics/001.toml"
words = getWords(url)

#generate audio files
files = ttsmp3Com(words)
#concatunate audio files
resultMp3 = concatunateFiles(files)
duration = getDuration(resultMp3)

#update rss
updateRss(words, resultMp3, duration, getTitle(url), getAuthor(url))

