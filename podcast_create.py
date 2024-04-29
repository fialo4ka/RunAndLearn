import itertools
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
    if language == 1:
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
            files.append(downloadMp3(str(i) + "_syn_de", "synonyme   "+ word.syn, 1))
        if word.kon: 
            files.append(downloadMp3(str(i) + "_kon_de", " " + word.kon.pres + ", " + word.kon.prat + ", " + word.kon.perfekt, 1))
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


samplerate = 44100

def fanzyConcatFiles(files, title) -> str:
    result = f"build/mp3/{title}.mp3"

    print(files)
    p_out = subprocess.Popen(['ffmpeg', '-f', 's16le', '-i', '-', result], stdin=subprocess.PIPE)

    for file in files:
        p = subprocess.run(['ffmpeg', '-i', file, '-ar', str(samplerate), '-f', 's16le', '-'], capture_output=True)
        if p.returncode != 0:
            raise Exception(f'{p=} failed')
        print(p.stderr.decode())

        data = p.stdout
        p_out.stdin.write(data)
        if "de" in file:
            p_out.stdin.write(bytes([0]*len(data)))
        else:
            p_out.stdin.write(bytes([0]*16))


    # p.communicate(input=data)
    p_out.stdin.flush()
    p_out.stdin.close()
    p_out.wait()
    return result

import lxml.etree as etree
from datetime import datetime
'''


def updateRss1(words : Word, resultMp3, duration, title, author) -> None:
    from feedgen.feed import FeedGenerator
    fg = FeedGenerator()
    fg.id('http://lernfunk.de/media/654321')
    fg.title('Some Testfeed')
    fg.author( {'name':'John Doe','email':'john@example.de'} )
    fg.link( href='http://example.com', rel='alternate' )
    fg.logo('http://ex.com/logo.jpg')
    fg.subtitle('This is a cool feed!')
    fg.link( href='http://larskiesow.de/test.atom', rel='self' )
    fg.language('en')
    fe = fg.add_entry()
    fe.id('http://lernfunk.de/media/654321/1')
    fe.title('The First Episode')
    fe.link(href="http://lernfunk.de/feed")
    fg.contributor( name='John Doe', email='jdoe@example.com' )
    fe.description('Enjoy our first episode.')
    fe.enclosure('http://lernfunk.de/media/654321/1/file.mp3', 0, 'audio/mpeg')
    fg.rss_str(pretty=True)
    fg.rss_file('rss.xml') # Write the RSS feed to a file

'''
def summaryHtml(words : Word):
    str = ''
    for word in words:
        str = f'{str}<br>{word.de} - {word.ru}'
        if word.syn: 
            str = f'{str}<br>synonyme:{word.syn}'
        if word.kon: 
            str = f'{str}<br>Präsens:{word.kon.pres}, Präteritum: {word.kon.prat}, Perfekt: {word.kon.perfekt}'
        for example in word.ex:
            str = f'{str}<br>{example.de} - {example.ru}'
        str = f'{str}<br>'
    return str

def updateRss(words : Word, resultMp3, duration, title, author) -> None:
    xmlfilepath='build/podcast.xml' 
    tree = etree.parse(xmlfilepath)
    print(etree.tostring(tree, pretty_print=True))
    channel = tree.getroot()
    print(channel)
    dateNow = datetime.now().strftime("%d/%m/%Y, %H:%M")
    item = etree.SubElement(channel, 'entry')
    etree.SubElement(item, 'author').text = author  
    etree.SubElement(item, 'title').text = title
    etree.SubElement(item, 'summary').text =  summaryHtml(words) 
    etree.SubElement(item, 'updated').text = dateNow   
    etree.SubElement(item, 'link', href=f'https://de.fialo.info/mp3/{title}.mp3', rel="enclosure", length=str(getDurationMs(resultMp3)), type="audio/mpeg").text = ''  
    etree.SubElement(item, 'id').text = f'urn:uuid:1225c695-cfb8-asde-aaaa-{datetime.now().strftime("%d%m%Y%H%M")}'
    item.insert(1, item[-1])    
    date = tree.xpath('//feed/updated') 
    print(date)
    #date[0].text = dateNow
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


from bs4 import BeautifulSoup as Soup

def htmlTableRow(soup, table, word_de, word_ru):
    new_tr = soup.new_tag("tr")
    new_td1 = soup.new_tag("td")
    new_td2 = soup.new_tag("td")
    new_td1.string = word_de
    new_td2.string = word_ru
    new_tr.append(new_td1)
    new_tr.append(new_td2)
    table.append(new_tr)
    return table

def htmlTable(words, soup, table):
    for word in words:
        table = htmlTableRow(soup, table, word.de, word.ru)
        if word.syn: 
            table = htmlTableRow(soup, table, "synonyme: "+ word.syn,'')
        if word.kon: 
            table = htmlTableRow(soup, table, " " + word.kon.pres + ", " + word.kon.prat + ", " + word.kon.perfekt,'')
        for example in word.ex:
            table =  htmlTableRow(soup, table, example.de,  example.ru)
    return table

def updateHtml(title, author, words : Word):
    htmlfilepath='build/index.html' 
    html = ''
    with open(htmlfilepath, 'r') as file:
        html = file.read()
    soup = Soup(html, 'lxml')
    entry_place = soup.find("hr", {"id": "entry_place"}) 
    h2 = soup.new_tag('h2', {"id": title}, **{'class':'w3-center'})
    h2.string = title
    entry_place.insert_before(h2)
    h5 = soup.new_tag('h5', **{'class':'w3-center'})
    h5.string = f'Author {author}' 
    entry_place.insert_before(h5)
    table = soup.new_tag('table', **{'class':'w3-table-all w3-card-4'})
    table = htmlTable(words, soup, table)
    entry_place.insert_before(table)
    with open(htmlfilepath, "w") as file:
        file.write(str(soup))
    

########
# MAIN #
########


#load toml
url = "topics/004.toml"
title = getTitle(url)
author = getAuthor(url)
words = getWords(url)
#generate audio files
files = ttsmp3Com(words)
#concatunate audio files
resultMp3 = fanzyConcatFiles(files, title)
duration = getDurationStr(resultMp3)
#update rss
updateRss(words, resultMp3, duration, title, author)
#update html
updateHtml(title, author, words)

''''''

#############
#test
############

#1. all files in 1 mp3

#files = test()
#resultMp3 = fanzyConcatFiles(files, title)

#2. Rss
# url = "topics/002.toml"
# words = getWords(url)
# title = getTitle(url)
# author = getAuthor(url)
# duration = getDurationStr('build/mp3/001.mp3')
# updateRss(words, "build/mp3/001.mp3", duration, title, author)

#3 Html generation

# url = "topics/002.toml"
# title = getTitle(url)
# author = getAuthor(url)
# words = getWords(url)
# updateHtml(title, author, words)