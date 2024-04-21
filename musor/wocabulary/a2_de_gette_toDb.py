import sqlite3
import string

def insert_word(conn, content, type, artikl):
    verb = (content, type, artikl)
    sql = ''' INSERT INTO Words(Word,TypeId, Artikl)
              VALUES(?,?,?) '''
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

def search_word(conn, content):
    sql = " select id from Words where TRIM(upper(Word)) = TRIM(upper( ? )) "
    cur = conn.cursor()
    cur.execute(sql, (content, ))
    rows = cur.fetchall()
    if len(rows) == 0:
        print(content + ' alredy exist in Words')
        return None
    sql = '''select WordId from Verbs where TRIM(upper(Prasens))  = TRIM(upper(?)) or TRIM(upper(Prateritum))  = TRIM(upper(?)) or TRIM(upper(Perfekt))  = TRIM(upper(?)) '''
    cur = conn.cursor()
    cur.execute(sql, (content, content, content))
    rows = cur.fetchall()    
    if len(rows) == 0:
        print(content + ' alredy exist in Verbs')
        return None
    
def detect_articl(content):
    if 'DER ' in content.upper():
        return 'der'
    if 'DAS ' in content.upper():
        return 'das'
    if 'DIE ' in content.upper():
        return 'die'
    return None

def string_analize_save(content):
    connection = db_connection()
    id = search_word(connection, content)
    if id is not None:
        return
    articl = detect_articl(content)
    if articl is not None:
        type = 2
    else:  
        type = 3
    id = insert_word(connection, content, type, articl)


def printable_word(str):
    str = str.strip('\n')
    return str.removeprefix(' ')

file = open('/home/fialo4ka/workspace/RunAndLearn/wocabulary/a2_de_gette.txt','r')
while True:
    content = file.readline()   
    if not content:
        break                 
    string_analize_save(printable_word(content))
file.close()


