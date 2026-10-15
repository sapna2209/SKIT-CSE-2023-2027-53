import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "potholes.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

def create_database():
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"Database created at: {DB_PATH}")

if __name__ == "__main__":
    create_database()