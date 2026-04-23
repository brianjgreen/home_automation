#!/usr/bin/env python3

import argparse
import hashlib
import json
import shutil
import subprocess
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

# Requires Python 3.11+ and exiftool
DB_FILENAME = ".photo_index.db"

def get_db_connection(archive_dir: Path) -> sqlite3.Connection:
    db_path = archive_dir / DB_FILENAME
    conn = sqlite3.connect(db_path)
    # Create the table if it doesn't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS photo_index (
            hash TEXT PRIMARY KEY,
            file_path TEXT NOT NULL
        )
    ''')
    return conn

def compute_file_hash(path: Path) -> str:
    """Compute SHA-256 using optimized file_digest."""
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

def heic_metadata(path: Path):
    result = subprocess.run(["exiftool", "-json", str(path)], capture_output=True, text=True)
    try:
        return json.loads(result.stdout)[0]
    except (IndexError, json.JSONDecodeError):
        return {}

def extract_exif_datetime(path: Path) -> Optional[datetime]:
    creation_tags = ["DateTimeOriginal", "CreateDate", "DateTime"]
    metadata = heic_metadata(path)
    for tag in creation_tags:
        value = metadata.get(tag)
        if value:
            try:
                return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
            except ValueError:
                continue
    return None

def determine_photo_date(path: Path) -> datetime:
    exif_dt = extract_exif_datetime(path)
    if exif_dt:
        return exif_dt
    return datetime.fromtimestamp(path.stat().st_mtime)

def is_duplicate(conn: sqlite3.Connection, file_hash: str) -> Optional[str]:
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM photo_index WHERE hash = ?", (file_hash,))
    row = cursor.fetchone()
    return row[0] if row else None

def archive_photo(src: Path, archive_root: Path, conn: sqlite3.Connection, dry_run: bool):
    file_hash = compute_file_hash(src)
    
    existing_path = is_duplicate(conn, file_hash)
    if existing_path:
        print(f"Duplicate detected, skipping: {src.name} (exists at {existing_path})")
        return

    dt = determine_photo_date(src)
    dest_dir = archive_root / f"{dt.year}" / f"{dt.month:02d}"
    
    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)
    
    dest_file = dest_dir / src.name

    if dry_run:
        print(f"[DRY RUN] Would copy: {src.name} → {dest_file}")
    else:
        shutil.copy2(src, dest_file)
        # Update SQLite immediately after successful copy
        conn.execute(
            "INSERT INTO photo_index (hash, file_path) VALUES (?, ?)", 
            (file_hash, str(dest_file))
        )
        conn.commit()
        print(f"Copied: {src.name} → {dest_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Import photos to SQLite-indexed archive."
    )
    parser.add_argument("import_dir", type=Path, help="Source directory")
    parser.add_argument("archive_dir", type=Path, help="Archive directory")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions")

    args = parser.parse_args()

    if not args.archive_dir.exists() and not args.dry_run:
        args.archive_dir.mkdir(parents=True)

    conn = get_db_connection(args.archive_dir)

    try:
        for path in args.import_dir.rglob("*"):
            if path.is_file() and path.name != ".DS_Store":
                archive_photo(path, args.archive_dir, conn, args.dry_run)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
