import sqlite3
from pathlib import Path
DB_PATH = Path(__file__).resolve().parents[1] / "civicsignal.db"
def connect():
    conn=sqlite3.connect(DB_PATH); conn.row_factory=sqlite3.Row; return conn
def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,description TEXT NOT NULL,
        category TEXT NOT NULL,neighborhood TEXT NOT NULL,latitude REAL NOT NULL,longitude REAL NOT NULL,
        severity INTEGER NOT NULL,public_impact INTEGER NOT NULL,priority_score REAL NOT NULL,
        priority_level TEXT NOT NULL,priority_explanation TEXT NOT NULL,duplicate_of INTEGER,
        duplicate_similarity REAL DEFAULT 0,status TEXT NOT NULL DEFAULT 'Open',created_at TEXT NOT NULL)""")
        c.commit()
