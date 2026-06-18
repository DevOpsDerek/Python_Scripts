"""
find_large_files.py — Find the biggest files under a directory tree
====================================================================
Concepts covered:
  - os.walk()        (recursive directory traversal)
  - heapq            (efficient top-N selection without sorting everything)
  - pathlib.Path     (cross-platform paths)
  - Generator functions (yield)
  - Type hints
"""

import heapq
import os
from datetime import datetime
from pathlib import Path
from typing import Generator


def format_size(size_bytes: int) -> str:
    """Return a human-readable file size string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def walk_files(root: Path) -> Generator[Path, None, None]:
    """Yield every file under *root*, skipping permission errors.

    This is a *generator* — it produces one file path at a time rather than
    building a giant list in memory. Great for large directory trees!

    Args:
        root: The top-level directory to walk.

    Yields:
        Path objects for every file found.
    """
    for dirpath, _dirnames, filenames in os.walk(root):
        for filename in filenames:
            yield Path(dirpath) / filename  # "/" operator joins path segments


def find_large_files(
    directory: str = ".",
    top_n: int = 20,
    min_size_mb: float = 0.0,
) -> None:
    """Print the N largest files under a directory tree.

    Uses heapq.nlargest() which is more efficient than sorting the full list
    when you only need the top N results.

    Args:
        directory:   Root directory to search.
        top_n:       How many files to show.
        min_size_mb: Only show files larger than this many megabytes.
    """
    root = Path(directory).resolve()

    if not root.exists():
        print(f"❌ Directory not found: {root}")
        return

    min_bytes = int(min_size_mb * 1024 * 1024)

    print(f"\n🔍 Searching for large files in: {root}")
    print(f"   Minimum size: {format_size(min_bytes) if min_bytes else 'none'}")
    print("   (This may take a moment for large trees…)\n")

    # Build a list of (size, path) tuples for files above the minimum size.
    # heapq.nlargest picks the top N by the first element of each tuple.
    file_sizes = []
    scanned = 0

    for file_path in walk_files(root):
        scanned += 1
        try:
            size = file_path.stat().st_size
        except (OSError, PermissionError):
            # Some files may not be accessible — skip them gracefully
            continue

        if size >= min_bytes:
            file_sizes.append((size, file_path))

    # heapq.nlargest is O(n log k) — faster than sorting when k << n
    largest = heapq.nlargest(top_n, file_sizes, key=lambda t: t[0])

    if not largest:
        print("   No files found matching the criteria.")
        return

    print(f"{'Rank':<5} {'Size':>10}  {'Path'}")
    print("-" * 80)

    for rank, (size, path) in enumerate(largest, start=1):
        # Get last-modified time for extra context
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")
        except OSError:
            mtime = "unknown"

        print(f"{rank:<5} {format_size(size):>10}  {path}  ({mtime})")

    print("-" * 80)
    print(f"\n   Scanned {scanned:,} files. Showing top {len(largest)}.\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Find the largest files under a directory.")
    parser.add_argument("directory", nargs="?", default=".", help="Root directory to search")
    parser.add_argument("-n", "--top", type=int, default=20, help="Number of files to show (default: 20)")
    parser.add_argument("-m", "--min-mb", type=float, default=0.0, help="Minimum file size in MB (default: 0)")

    args = parser.parse_args()
    find_large_files(args.directory, top_n=args.top, min_size_mb=args.min_mb)

# ---------------------------------------------------------------------------
# TRY THIS:
#   python find_large_files.py ~           # find largest files in home dir
#   python find_large_files.py / -n 10    # top 10 largest on the whole system
#   python find_large_files.py . -m 1     # only files larger than 1 MB
# ---------------------------------------------------------------------------
