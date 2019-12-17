import sqlite3
import sys


def create_table():
    conn = sqlite3.connect('./wordlist.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE wordlist
        (id INTEGER PRIMARY KEY, word TEXT, sorted_word TEXT)''')
    conn.commit()
    conn.close()

with open('./wordlist.txt','r') as f:
    conn = sqlite3.connect('./wordlist.db')
    c = conn.cursor()
    words = (s.strip() for s in f.readlines())

    for word in words:
        sorted_word = ''.join(sorted(word))
        c.execute('INSERT INTO wordlist(word, sorted_word) VALUES(?,?);',(word, sorted_word))
    conn.commit()
    conn.close()
