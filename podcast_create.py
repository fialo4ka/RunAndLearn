import tomllib
from dataclasses import dataclass, field
from typing import Any, Optional
import subprocess

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
import os

def postequest(dataText, language) -> str:
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

def getMp3(fileName, local_filename) -> str:
    temp = "temp"
    if not os.path.exists(temp):
        os.makedirs(temp)
    local_filename = temp + "/" + local_filename + ".mp3"
    with requests.get(fileName, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return local_filename


def downloadMp3(local_filename, text, language) -> str:
    fileName = postequest(text, language)
    local_filename = getMp3(fileName, local_filename)
    return local_filename

def ttsmp3Com(data) -> list[str]:
    files = []
    i = 0
    for word in data:
        files.append(downloadMp3(str(i) + "_de", word.de, 1))
        files.append(downloadMp3(str(i) + "_ru", word.ru, 0))
        if word.syn: 
            files.append(downloadMp3(str(i) + "_syn", word.syn, 0))
        if word.kon: 
            files.append(downloadMp3(str(i) + "_kon", ": " + word.kon.pres + ", : " + word.kon.prat + ", : " + word.kon.perfekt, 0))
        j = 0
        for example in word.ex:
            files.append(downloadMp3(str(i) + "_" + str(j) + "_x_de", "   " + example.de, 1))
            files.append(downloadMp3(str(i) + "_" + str(j) + "_x_ru", "   " + example.ru, 0))
            j = j +1
        i = i + 1
    return files


def getDurationStr(resultMp3) -> str:
    p = subprocess.run(['ffmpeg -i ' + resultMp3 + ' 2>&1 | awk \'/Duration/ { print substr($2,0,length($2)-1) }\''], shell=True, capture_output=True)
    return p.stdout.decode().strip()

import time

def getDurationMs(resultMp3) -> int:
    str = getDurationStr(resultMp3)
    hours_str, minutes_str, seconds_str = (["0", "0"] + str.split(":"))[-3:]
    hours = int(hours_str)
    minutes = int(minutes_str)
    seconds = float(seconds_str)
    return int(3600000 * hours + 60000 * minutes + 1000 * seconds)


def concatunateFile(file1: str , file2: str, result: str) -> None:
    duration = getDurationMs(file1)
    command = ['ffmpeg', '-i', file1, '-i', file2, '-filter_complex' ,f'[0]adelay=0[a0];[1]adelay={duration}[a1];[a0][a1]amix=inputs=2', result]
    p = subprocess.run(command)
    if p.returncode != 0:
        raise Exception(f'{p=} failed')

def concatunateFiles(files, title) -> str:
    mp3 = "mp3"
    if not os.path.exists(mp3):
        os.makedirs(mp3)
    result = f"{mp3}/{title}.mp3"
    param = []
    delay = '' 
    delay2 =''  
    i = 0
    totalDelay = 0
    for file in files:
        param.append('-i')
        param.append(file)
        delay = f'{delay}[{i}]adelay={totalDelay}[a{i}];'
        delay2 = f'{delay2}[a{i}]'
        i= i + 1
        if "de" in file:
            totalDelay += getDurationMs(file)*2
        else:
            totalDelay += getDurationMs(file)
    delay2 = f'{delay}{delay2}amix=inputs={i}'    
    print(delay2)
    command = ['ffmpeg', *param, '-filter_complex', delay2, result]   
    print(command)
    p = subprocess.run(command)
    if p.returncode != 0:
        raise Exception(f'{p=} failed')
    return result


'''
    result_old = files[0]
    for i, file in enumerate(files[1:]):
        result = f"mp3/{title}_{i}.mp3"
        concatunateFile(result_old, file, result)
        result_old = result

    return result_old
'''

#ffmpeg -i temp/0_de.mp3 -i temp/0_ru.mp3 -filter_complex "[0]adelay=0[a0];[1]adelay=2000[a1];[a0][a1]amix=inputs=2" mp3/001.mp3
#ffmpeg -i temp/0_de.mp3 -f null
#ffmpeg -i temp/0_de.mp3 2>&1 | grep Duration
#ffmpeg -i temp/0_de.mp3 2>&1 | awk '/Duration/ { print substr($2,0,length($2)-1) }'


import lxml.etree as etree
from datetime import datetime

def updateRss(words, resultMp3, duration, title, author) -> None:
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
        filetowrite.write('<?xml version=\"1.0\" encoding=\"UTF-8\"?>'.encode() +    etree.tostring(tree, pretty_print=True)     ) 
        filetowrite.close()

def getTitle(fileName: str):
    list = fileName.split('/')
    return list[len(list)-1].replace('.toml', '')

def test():
    dir_list = os.listdir("temp")
    # prints all files
    result = []
    for file in dir_list:
        result.append("temp/" + file)
    return result


#load toml
url = "topics/001.toml"
title = getTitle(url)
author = getAuthor(url)
words = getWords(url)

#generate audio files

files = ttsmp3Com(words)

#files = test()#['0_ru.mp3', '0_de.mp3', '0_syn.mp3', '0_0_x_ru.mp3', '0_0_x_de.mp3', '0_1_x_ru.mp3', '0_1_x_de.mp3', '0_2_x_ru.mp3']


#concatunate audio files
resultMp3 = concatunateFiles(files, title)
duration = getDurationStr(resultMp3)

#update rss
updateRss(words, resultMp3, duration, title, author)

