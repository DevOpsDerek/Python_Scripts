"""
Exercise 01 — File Extension Report
=====================================
GOAL: Write a script that scans a directory and prints a report showing
how many files of each type (extension) exist, sorted by count.

Expected output example:
    File Extension Report: /home/user/Documents
    ─────────────────────────────────────────────
    .pdf          42 files  ████████████████████
    .docx         18 files  █████████
    .txt          15 files  ███████
    .png          10 files  █████
    (no ext)       3 files  █

CONCEPTS YOU WILL PRACTISE:
  - pathlib.Path.rglob()   — recursive file search
  - collections.Counter    — counting occurrences
  - String formatting      — aligning columns
  - Sorting a Counter      — .most_common()

HOW TO RUN:
    python exercise.py                  (scans current directory)
    python exercise.py ~/Documents      (scans a specific directory)
"""

import sys
from collections import Counter
from pathlib import Path


def get_extension(path: Path) -> str:
    """Return the file extension as a lowercase string.

    Files with no extension should return the string '(no ext)'.

    Hint: Path objects have a .suffix attribute that returns the extension
    including the dot, e.g. '.pdf'. It returns '' for files with no extension.

    Args:
        path: A Path object pointing to a file.

    Returns:
        The extension string, e.g. '.pdf' or '(no ext)'.
    """
    # TODO: Get path.suffix and convert it to lowercase.
    # If the suffix is an empty string, return '(no ext)' instead.
    # Remove the pass below and write your code here.
    pass


def count_extensions(directory: str) -> Counter:
    """Scan a directory recursively and count files by extension.

    Args:
        directory: The root directory to scan.

    Returns:
        A Counter mapping extension string → file count.

    Hint: Use Path(directory).rglob('*') to find all files recursively.
    Remember to skip directories — only count files (use .is_file()).
    """
    # TODO: Create a Path object from the directory string.
    # TODO: Use rglob('*') to iterate over all entries.
    # TODO: For each entry that is a file (not a directory), get its extension.
    # TODO: Count extensions with a Counter.
    # TODO: Return the Counter.
    pass


def render_bar(count: int, max_count: int, width: int = 20) -> str:
    """Draw a proportional bar chart using '█' characters.

    The bar should be proportional: if count == max_count, the bar is full
    (width characters). Smaller counts get proportionally shorter bars.

    Args:
        count:     This file type's count.
        max_count: The highest count of any file type (for scaling).
        width:     Maximum bar length in characters.

    Returns:
        A string of '█' characters.

    Hint: filled = int(count / max_count * width)
    """
    # TODO: Calculate how many '█' characters to draw.
    # TODO: Return a string of that many '█' characters.
    pass


def print_report(directory: str, counts: Counter) -> None:
    """Print the formatted report.

    Args:
        directory: The scanned directory path (for the header).
        counts:    Counter of extension → count.
    """
    print(f"\n  File Extension Report: {directory}")
    print("  " + "─" * 50)

    if not counts:
        print("  No files found.")
        return

    # TODO: Find the maximum count (needed for scaling the bar chart).
    # Hint: max_count = counts.most_common(1)[0][1]
    max_count = None  # Replace this with your code

    # TODO: Iterate over counts.most_common() and print each row.
    # Format each row like this (use f-strings and string padding):
    #   {extension:<12} {count:>5} files  {bar}
    # Example: .pdf            42 files  ████████████████████
    for extension, count in counts.most_common():
        bar = render_bar(count, max_count)
        # TODO: Print the formatted row.
        pass

    print(f"\n  Total: {sum(counts.values())} files across {len(counts)} extension(s)\n")


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    extension_counts = count_extensions(target)
    print_report(target, extension_counts)


# ── HINTS (read only if stuck!) ───────────────────────────────────────────────
# 1. Path.suffix returns '' for files like 'Makefile' with no extension.
# 2. Counter({'a': 3, 'b': 1}).most_common() returns [('a',3), ('b',1)].
# 3. f"{'hello':<12}" pads 'hello' to 12 characters wide (left-aligned).
# 4. f"{42:>5}" pads 42 to 5 characters wide (right-aligned).
