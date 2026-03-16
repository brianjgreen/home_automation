# Photo Archive

Note: Optimized for Python 3.14

- Scan import directory
- Read EXIF data
- Generate photo file hash
- Move to $Archive/$Year/$Month
  - if no duplicate hashes, else leave in imports
  - check for duplicate filenames, save both if not same hash
- Save data file with hashes

## Usage

```bash
photo_archive.py [-h] [--dry-run] import_dir archive_dir
```

### Help

```bash
usage: photo_archive.py [-h] [--dry-run] import_dir archive_dir

Import photos and archive them by Year/Month with duplicate detection.

positional arguments:
  import_dir   Directory containing photos to import
  archive_dir  Destination archive directory

options:
  -h, --help   show this help message and exit
  --dry-run    Simulate actions without copying files
```
