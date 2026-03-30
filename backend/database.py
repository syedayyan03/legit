import sqlite3
import os
from datetime import datetime

DATABASE_PATH = os.path.join('database', 'users.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists('database'):
        os.makedirs('database')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # job_scans table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        url TEXT NOT NULL,
        prediction TEXT NOT NULL,
        confidence REAL NOT NULL,
        type TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # scan_details table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scan_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER,
        job_text TEXT,
        risk_score REAL,
        remote BOOLEAN,
        benefits TEXT,
        FOREIGN KEY (scan_id) REFERENCES job_scans (id)
    )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
