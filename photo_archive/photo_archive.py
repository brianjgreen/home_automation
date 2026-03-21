#!/usr/bin/env python3

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

# Note: This script requires Python 3.11+ for hashlib.file_digest and exiftool to be installed and in PATH.
# sudo apt install libimage-exiftool-perl


INDEX_FILENAME = ".photo_hash_index.json"


def load_hash_index(archive_dir: Path) -> dict:
    index_path = archive_dir / INDEX_FILENAME
    if index_path.exists():
        try:
            with index_path.open("r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_hash_index(archive_dir: Path, index: dict, dry_run: bool):
    if dry_run:
        print("[DRY RUN] Would update hash index")
        return

    index_path = archive_dir / INDEX_FILENAME
    with index_path.open("w") as f:
        json.dump(index, f, indent=2)


def compute_file_hash(path: Path) -> str:
    """Compute SHA-256 using optimized file_digest (Python 3.11+)."""
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def heic_metadata(path):
    result = subprocess.run(["exiftool", "-json", path], capture_output=True, text=True)
    return json.loads(result.stdout)[0]


def extract_exif_datetime(path: Path) -> Optional[datetime]:
    creation_tags = ["DateTimeOriginal", "CreateDate", "DateTime"]
    for tag_id, value in heic_metadata(path).items():
        if tag_id in creation_tags:
            try:
                return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
            except Exception:
                print(f"Warning: Failed to parse EXIF date '{value}' for {path}, skipping EXIF date. Error: {e}")
                return None
    print(f"Warning: No valid EXIF date found for {path}, falling back to file modification time.")
    return None


def determine_photo_date(path: Path) -> datetime:
    exif_dt = extract_exif_datetime(path)
    if exif_dt:
        return exif_dt

    return datetime.fromtimestamp(path.stat().st_mtime)


def archive_photo(src: Path, archive_root: Path, index: dict, dry_run: bool):
    file_hash = compute_file_hash(src)

    if file_hash in index:
        print(f"Duplicate detected, skipping: {src} (matches {index[file_hash]})")
        return

    dt = determine_photo_date(src)
    year = f"{dt.year}"
    month = f"{dt.month:02d}"

    dest_dir = archive_root / year / month
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_file = dest_dir / src.name

    if dry_run:
        print(f"[DRY RUN] Would copy: {src} → {dest_file}")
    else:
        shutil.copy2(src, dest_file)
        print(f"Copied: {src} → {dest_file}")

    index[file_hash] = str(dest_file)


def main():
    parser = argparse.ArgumentParser(
        description="Import photos and archive them by Year/Month with duplicate detection."
    )
    parser.add_argument(
        "import_dir", type=Path, help="Directory containing photos to import"
    )
    parser.add_argument("archive_dir", type=Path, help="Destination archive directory")
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulate actions without copying files"
    )

    args = parser.parse_args()

    index = load_hash_index(args.archive_dir)

    # Faster directory scanning
    for path in args.import_dir.rglob("*"):
        if path.is_file():
            archive_photo(path, args.archive_dir, index, args.dry_run)

    save_hash_index(args.archive_dir, index, args.dry_run)


if __name__ == "__main__":
    main()
