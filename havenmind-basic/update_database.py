import sqlite3
import os

def update_database():
    # Remove old database to recreate with new schema
    if os.path.exists('havenmind.db'):
        os.remove('havenmind.db')
        print("Removed old database")
    
    # Create new database with updated schema
    conn = sqlite3.connect('havenmind.db')
    c = conn.cursor()
    
    # Users table with authentication fields
    c.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'student',
        is_verified BOOLEAN DEFAULT 0,
        reset_token TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        cognitive_load_score REAL DEFAULT 0.0
    )''')
    
    # Journal entries table
    c.execute('''CREATE TABLE journal_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        sentiment_score REAL,
        emotion_tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Calendar events table
    c.execute('''CREATE TABLE calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        event_date TIMESTAMP NOT NULL,
        stress_level TEXT DEFAULT 'medium',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Support sessions table
    c.execute('''CREATE TABLE support_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1_id INTEGER NOT NULL,
        user2_id INTEGER,
        session_type TEXT DEFAULT 'peer',
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()
    print("Database updated successfully with new schema!")

if __name__ == '__main__':
    update_database()