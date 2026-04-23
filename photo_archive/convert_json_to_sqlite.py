import sqlite3
import json
from pathlib import Path
import argparse

DB_FILENAME = ".photo_index.db"
JSON_FILENAME = ".photo_hash_index.json"

def migrate_json_to_sqlite(archive_dir: Path):
    json_path = archive_dir / JSON_FILENAME
    db_path = archive_dir / DB_FILENAME

    if not json_path.exists():
        print(f"No JSON index found at {json_path}. Nothing to migrate.")
        return

    # Load existing data
    print(f"Reading {json_path}...")
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Connect to SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            hash TEXT PRIMARY KEY,
            file_path TEXT NOT NULL
        )
    ''')

    # Insert data
    print(f"Migrating {len(data)} records to SQLite...")
    records = [(h, p) for h, p in data.items()]
    
    cursor.executemany('INSERT OR REPLACE INTO photos (hash, file_path) VALUES (?, ?)', records)
    
    conn.commit()
    conn.close()
    print(f"Migration complete. Database created at {db_path}")
    print(f"You can now safely delete {json_path} after verifying the script below works.")

def get_db_connection(archive_dir: Path):
    return sqlite3.connect(archive_dir / DB_FILENAME)

# --- REPLACEMENT FUNCTIONS FOR YOUR ORIGINAL SCRIPT ---

def check_duplicate(conn, file_hash: str) -> bool:
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM photos WHERE hash = ?", (file_hash,))
    result = cursor.fetchone()
    return result[0] if result else None

def save_to_db(conn, file_hash: str, dest_path: str):
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO photos (hash, file_path) VALUES (?, ?)", (file_hash, dest_path))
    conn.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate Photo Index to SQLite")
    parser.add_argument("archive_dir", type=Path, help="Archive directory containing the JSON index")
    args = parser.parse_args()
    
    migrate_json_to_sqlite(args.archive_dir)
