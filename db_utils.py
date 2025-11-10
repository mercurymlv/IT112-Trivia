# db_utils.py
import sqlite3
import os

def get_db_connection():
    """Create a database connection with absolute path."""
    db_path = os.getenv("TRIVIA_DB_PATH", "trivia.db")  # fallback for local dev
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # optional: lets you access columns by name
    return conn
