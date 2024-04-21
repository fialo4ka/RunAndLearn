import sqlite3
import string

def insert_word(conn, content, type):
    verb = (content, type)
    sql = ''' INSERT INTO Words(Word,TypeId)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, verb)
    conn.commit()
    return cur.lastrowid

def insert_verb(conn, id, wordList):
    verb = (id, wordList[1], wordList[2], wordList[3])
    sql = ''' INSERT INTO Verbs(WordId, Prasens, Prateritum, Perfekt)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, verb)
    conn.commit()
    return cur.lastrowid


def db_connection():
    db_file = "/home/fialo4ka/workspace/RunAndLearn/words.db"
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn



def string_analize_save(wordList):
    connection = db_connection()
    id = insert_word(connection, wordList[0], 1)
    insert_verb(connection, id, wordList)


def printable_word(str):
    str = str.strip('\n')
    return str.removeprefix(' ')

file = open('/home/fialo4ka/workspace/RunAndLearn/wocabulary/all_verbs.txt','r')
content = file.readline()
while True:   
    if not content:
        break        
    wordList = []     
    for x in range(4):
        wordList.insert(x, printable_word(content))
        content = file.readline() 
    print(wordList)         
    string_analize_save(wordList)
file.close()


