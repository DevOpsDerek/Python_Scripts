"""
Exercise 09 — Directory Size Report
======================================
GOAL: Write a script that calculates the total size of each immediate
subdirectory inside a target directory, then prints them sorted by size.

Expected output example:
    Directory Size Report: /home/user
    ─────────────────────────────────────────────────────────
    Rank  Size        Files   Directory
    ─────────────────────────────────────────────────────────
       1  12.3 GB     4,201   Downloads
       2   3.1 GB       892   Videos
       3   1.4 GB    12,043   .local
       4 500.2 MB     3,112   Documents
    ─────────────────────────────────────────────────────────
    Total: 17.3 GB across 5 directories

CONCEPTS YOU WILL PRACTISE:
  - os.walk()              — recursive directory traversal
  - Accumulating totals    — summing sizes as you walk
  - Sorting with key=      — sorting a list of dicts
  - Human-readable sizes   — bytes → MB/GB conversion

HOW TO RUN:
    python exercise.py ~
    python exercise.py /var
    python exercise.py . --top 5
"""

from pathlib import Path


def get_dir_size(directory: Path) -> tuple:
    """Calculate the total size and file count of a directory tree.

    Args:
        directory: Path object for the directory to measure.

    Returns:
        A tuple (total_bytes: int, file_count: int).

    Hint: Use os.walk(directory) to traverse the tree.
    For each file, get its size with os.path.getsize(full_path).
    Wrap in try/except (OSError, PermissionError) to skip inaccessible files.

    os.walk() yields (dirpath, dirnames, filenames).
    You only need dirpath and filenames.
    """
    total_bytes = 0
    file_count = 0

    # TODO: Walk the directory tree with os.walk(directory).
    # TODO: For each file in filenames, build the full path and get its size.
    # TODO: Add to total_bytes and increment file_count.
    # TODO: Return (total_bytes, file_count).
    pass


def bytes_to_human(b: int) -> str:
    """Return a human-readable size string."""
    # TODO: Convert bytes to the appropriate unit (B, KB, MB, GB, TB).
    # Return a string like '1.2 GB' or '450.0 MB'.
    # Hint: Divide by 1024 repeatedly until the value is < 1024.
    pass


def report(directory: str, top_n: int) -> None:
    """Print a sorted directory size report.

    Args:
        directory: Root directory to report on.
        top_n:     Show only the top N largest subdirectories (0 = all).
    """
    root = Path(directory)
    if not root.is_dir():
        print(f"  ❌ Not a directory: {root}")
        return

    print(f"\n  Scanning {root}  (this may take a moment…)")

    # Collect size data for each immediate subdirectory
    entries = []
    for child in root.iterdir():
        if child.is_dir():
            # TODO: Call get_dir_size(child) to get (size, count).
            # TODO: Append a dict with keys: name, size_bytes, file_count.
            pass

    # TODO: Sort entries by size_bytes, largest first.
    # Hint: entries.sort(key=lambda e: e['size_bytes'], reverse=True)

    if top_n:
        entries = entries[:top_n]

    print(f"\n  Directory Size Report: {root}")
    print("  " + "─" * 60)
    print(f"  {'Rank':<6} {'Size':>10}  {'Files':>8}   Directory")
    print("  " + "─" * 60)

    # TODO: Print each entry in the sorted list.
    # Use bytes_to_human() to format the size.
    # Format: f"  {rank:<6} {size_str:>10}  {count:>8,}   {name}"
    for rank, entry in enumerate(entries, start=1):
        pass  # Replace with your print statement

    total_bytes = sum(e["size_bytes"] for e in entries)
    total_files = sum(e["file_count"] for e in entries)
    print("  " + "─" * 60)
    print(
        f"  Total: {bytes_to_human(total_bytes)} across {len(entries)} director{'y' if len(entries) == 1 else 'ies'} ({total_files:,} files)\n"
    )


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Show subdirectory sizes.")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to scan (default: .)")
    parser.add_argument("--top", type=int, default=0, help="Show only the top N directories")
    args = parser.parse_args()

    report(args.directory, args.top)


# ── HINTS ─────────────────────────────────────────────────────────────────────
# 1. os.walk(path) yields (dirpath, dirnames, filenames).
#    `dirpath` is the current dir, `filenames` is a list of file names.
# 2. os.path.join(dirpath, filename) builds the full file path.
# 3. os.path.getsize(full_path) returns bytes — can raise OSError.
# 4. EXTENSION: Add a --hidden flag to include hidden directories (starting with .)
