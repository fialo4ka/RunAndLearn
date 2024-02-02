import sqlite3

def insert_verb(conn, content):
    verb = (content, 1)
    sql = ''' INSERT INTO Words(Word,type)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, verb)
    conn.commit()
    return cur.lastrowid


def db_connection(content):
    db_file = "/home/fialo4ka/workspace/RunAndLearn/words.db"
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    insert_verb(conn, content)
    return conn



def stringAnalizeSave(content):
    db_connection(content)


file = open('all_verbs.txt','r')
while True:        
    content = file.readline()
    if not content:
            break
    for x in range(4):
        wordList = []
        wordList.insert(x, content)
        stringAnalizeSave(content)
file.close()


