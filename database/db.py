import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

def get_connection():
    """Returns a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            age INTEGER,
            gender TEXT,
            weight REAL,
            height REAL,
            fitness_goal TEXT
        )
    ''')
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except Exception:
        pass
    
    # Create Workouts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATETIME DEFAULT CURRENT_TIMESTAMP,
            exercise TEXT NOT NULL,
            reps INTEGER NOT NULL,
            sets INTEGER NOT NULL,
            duration_seconds INTEGER NOT NULL,
            accuracy_score REAL,
            calories REAL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
