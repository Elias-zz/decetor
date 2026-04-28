import sqlite3
import os
from core.config import DATABASE_URL

def get_db_connection():
    db_path = DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db_path = DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensitive_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensitive_word TEXT NOT NULL UNIQUE
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_sensitive_word ON sensitive_words(sensitive_word)
    ''')
    
    conn.commit()
    conn.close()
    
    insert_test_data()

def insert_test_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    test_words = ["色情", "暴力", "毒品", "赌博", "诈骗"]
    
    for word in test_words:
        cursor.execute('SELECT id FROM sensitive_words WHERE sensitive_word = ?', (word,))
        if cursor.fetchone() is None:
            cursor.execute('INSERT INTO sensitive_words (sensitive_word) VALUES (?)', (word,))
    
    conn.commit()
    conn.close()
