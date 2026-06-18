"""
list_files.py — List files in a directory with useful details
=============================================================
Concepts covered:
  - pathlib.Path  (modern, object-oriented file paths)
  - os.stat       (file metadata: size, timestamps)
  - datetime      (converting timestamps to readable dates)
  - Sorting and filtering lists
  - f-strings and string formatting
"""

from datetime import datetime
from pathlib import Path


def format_size(size_bytes: int) -> str:
    """Convert a raw byte count into a human-readable string.

    Args:
        size_bytes: File size in bytes.

    Returns:
        A string like '1.23 MB' or '456 KB'.
    """
    # Define size thresholds in ascending order
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024  # Move to the next unit
    return f"{size_bytes:.1f} PB"


def list_files(directory: str = ".", show_hidden: bool = False) -> None:
    """List all files in a directory with size and last-modified date.

    Args:
        directory:   Path to the directory to list (defaults to current dir).
        show_hidden: If True, include files/dirs that start with a dot (.).
    """
    # pathlib.Path gives us a clean, cross-platform way to work with paths
    path = Path(directory).resolve()  # .resolve() turns relative paths into absolute ones

    if not path.exists():
        print(f"❌ Directory not found: {path}")
        return

    if not path.is_dir():
        print(f"❌ Not a directory: {path}")
        return

    print(f"\n📂 Contents of: {path}")
    print("-" * 70)
    # Column headers — using str.ljust() to left-align text in a fixed width
    print(f"{'Name':<40} {'Size':>10}  {'Last Modified'}")
    print("-" * 70)

    # Collect entries so we can sort them: directories first, then files
    dirs = []
    files = []

    for entry in path.iterdir():  # iterdir() yields Path objects for each item
        # Skip hidden entries (names starting with ".") unless requested
        if not show_hidden and entry.name.startswith("."):
            continue

        if entry.is_dir():
            dirs.append(entry)
        else:
            files.append(entry)

    # Sort each list alphabetically (case-insensitive)
    dirs.sort(key=lambda p: p.name.lower())
    files.sort(key=lambda p: p.name.lower())

    for entry in dirs + files:  # Directories first
        stat = entry.stat()  # Get file metadata (size, timestamps, permissions)

        # stat.st_mtime is a Unix timestamp (seconds since 1970-01-01)
        modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")

        if entry.is_dir():
            # Directories don't have a meaningful size; show a label instead
            name_display = f"📁 {entry.name}/"
            size_display = "[dir]"
        else:
            name_display = f"   {entry.name}"
            size_display = format_size(stat.st_size)

        print(f"{name_display:<40} {size_display:>10}  {modified}")

    print("-" * 70)
    print(f"  {len(dirs)} director{'y' if len(dirs) == 1 else 'ies'}, {len(files)} file{'s' if len(files) != 1 else ''}\n")


# ---------------------------------------------------------------------------
# Script entry point — only runs when executed directly, not when imported
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    # argparse makes it easy to accept command-line arguments
    parser = argparse.ArgumentParser(description="List files in a directory.")
    parser.add_argument(
        "directory",
        nargs="?",          # "?" means the argument is optional
        default=".",        # Default to the current working directory
        help="Directory to list (default: current directory)",
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",  # Sets the value to True when the flag is present
        help="Show hidden files and directories",
    )

    args = parser.parse_args()
    list_files(args.directory, show_hidden=args.all)

# ---------------------------------------------------------------------------
# TRY THIS:
#   python list_files.py                  # list current directory
#   python list_files.py /tmp             # list /tmp
#   python list_files.py ~ --all          # list home dir including hidden files
# ---------------------------------------------------------------------------
