"""
backup_files.py — Back up files/directories with timestamps and verification
=============================================================================
Concepts covered:
  - shutil         (high-level file operations: copy, archive)
  - datetime       (timestamped backup names)
  - pathlib.Path   (path manipulation)
  - Exception handling (try/except/finally)
  - Logging module (better than print() for real tools)
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Set up logging — the `logging` module is far better than print() for
# real tools because you can control verbosity, write to files, etc.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)  # Best practice: use module-level logger


def make_timestamp() -> str:
    """Return a filesystem-safe timestamp string, e.g. '2024-06-18_14-30-00'."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def backup_directory(source: str, destination: str, compress: bool = False) -> Path:
    """Copy an entire directory tree to a timestamped backup location.

    Args:
        source:      Path to the directory to back up.
        destination: Parent directory where the backup will be stored.
        compress:    If True, create a .tar.gz archive instead of a plain copy.

    Returns:
        Path to the created backup (directory or archive file).

    Raises:
        FileNotFoundError: If the source directory does not exist.
        NotADirectoryError: If the source path is not a directory.
    """
    src = Path(source).resolve()
    dest_parent = Path(destination).resolve()

    if not src.exists():
        raise FileNotFoundError(f"Source not found: {src}")
    if not src.is_dir():
        raise NotADirectoryError(f"Source is not a directory: {src}")

    # Build a unique backup name: <original_name>_backup_<timestamp>
    backup_name = f"{src.name}_backup_{make_timestamp()}"
    dest = dest_parent / backup_name

    # Ensure the destination parent exists (create it if needed)
    dest_parent.mkdir(parents=True, exist_ok=True)

    log.info("Starting backup: %s → %s", src, dest_parent)

    if compress:
        # shutil.make_archive(base_name, format, root_dir, base_dir)
        # Creates  <base_name>.tar.gz  containing everything under root_dir/base_dir
        archive_base = str(dest)
        log.info("Compressing to archive…")
        archive_path = shutil.make_archive(
            base_name=archive_base,
            format="gztar",  # gztar = .tar.gz
            root_dir=src.parent,  # The directory that contains src
            base_dir=src.name,  # The sub-directory to archive
        )
        result = Path(archive_path)
        size = result.stat().st_size
        log.info("✅ Archive created: %s (%.1f MB)", result, size / 1_048_576)
    else:
        # shutil.copytree copies an entire directory tree
        shutil.copytree(src, dest)
        # Calculate total size of the backup
        size = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file())
        result = dest
        log.info("✅ Backup created: %s (%.1f MB)", result, size / 1_048_576)

    return result


def backup_file(source: str, destination: str) -> Path:
    """Copy a single file to a timestamped backup.

    Args:
        source:      Path to the file to back up.
        destination: Directory where the backup copy will be stored.

    Returns:
        Path to the newly created backup file.
    """
    src = Path(source).resolve()

    if not src.exists():
        raise FileNotFoundError(f"File not found: {src}")
    if not src.is_file():
        raise ValueError(f"Not a regular file: {src}")

    dest_dir = Path(destination).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Insert the timestamp before the file extension: report.pdf → report_backup_2024-06-18.pdf
    stem = src.stem  # filename without extension
    suffix = src.suffix  # extension including the dot, e.g. '.pdf'
    backup_name = f"{stem}_backup_{make_timestamp()}{suffix}"
    dest = dest_dir / backup_name

    shutil.copy2(src, dest)  # copy2 also copies file metadata (timestamps, etc.)
    log.info("✅ File backed up: %s → %s", src, dest)
    return dest


def verify_backup(original: str, backup: str) -> bool:
    """Verify a backup by comparing file counts and total sizes.

    This is a quick sanity check, not a byte-for-byte comparison.
    For critical data, use find_duplicates.py to compare checksums.

    Args:
        original: Path to the original directory.
        backup:   Path to the backup directory.

    Returns:
        True if counts and sizes match, False otherwise.
    """
    orig_path = Path(original)
    back_path = Path(backup)

    orig_files = list(orig_path.rglob("*"))
    back_files = list(back_path.rglob("*"))

    orig_count = sum(1 for f in orig_files if f.is_file())
    back_count = sum(1 for f in back_files if f.is_file())

    orig_size = sum(f.stat().st_size for f in orig_files if f.is_file())
    back_size = sum(f.stat().st_size for f in back_files if f.is_file())

    log.info("Original: %d files, %.1f MB", orig_count, orig_size / 1_048_576)
    log.info("Backup:   %d files, %.1f MB", back_count, back_size / 1_048_576)

    if orig_count == back_count and orig_size == back_size:
        log.info("✅ Verification passed — file counts and sizes match.")
        return True
    else:
        log.warning("⚠️  Verification FAILED — mismatch detected!")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Backup files or directories.")
    parser.add_argument("source", help="File or directory to back up")
    parser.add_argument("destination", help="Where to store the backup")
    parser.add_argument("-z", "--compress", action="store_true", help="Create a .tar.gz archive")
    parser.add_argument("--verify", action="store_true", help="Verify the backup after creating it")
    args = parser.parse_args()

    src_path = Path(args.source)

    try:
        if src_path.is_dir():
            result = backup_directory(args.source, args.destination, compress=args.compress)
            if args.verify and not args.compress:
                verify_backup(args.source, str(result))
        else:
            result = backup_file(args.source, args.destination)
    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        log.error("❌ %s", e)
        raise SystemExit(1) from None

# ---------------------------------------------------------------------------
# TRY THIS:
#   python backup_files.py ~/Documents ~/Backups
#   python backup_files.py ~/Documents ~/Backups --compress
#   python backup_files.py ~/Documents ~/Backups --verify
#   python backup_files.py myfile.txt ~/Backups
# ---------------------------------------------------------------------------
