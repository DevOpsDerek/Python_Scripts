"""
Exercise 02 — Find Files by Pattern
=====================================
GOAL: Write a script that searches a directory tree for files whose
names match a wildcard pattern (like *.log or report_*.txt).

Expected output example:
    Searching for '*.py' in /home/user/projects
    ─────────────────────────────────────────────
    Found 12 match(es):

      /home/user/projects/app/main.py          (2.1 KB)
      /home/user/projects/app/utils.py         (0.8 KB)
      ...

CONCEPTS YOU WILL PRACTISE:
  - pathlib.Path.rglob()   — recursive search
  - fnmatch.fnmatch()      — wildcard pattern matching
  - Generators / yield     — memory-efficient iteration
  - argparse               — command-line arguments

HOW TO RUN:
    python exercise.py "*.py"
    python exercise.py "*.log" /var/log
    python exercise.py "report_*" ~/Documents
"""

import sys
from pathlib import Path


def find_files(directory: str, pattern: str):
    """Search *directory* recursively for files matching *pattern*.

    This should be a GENERATOR function (use `yield`, not `return`).
    Generators are memory-efficient: they produce one result at a time
    instead of building a list of all results in memory.

    Args:
        directory: Root directory to search.
        pattern:   Wildcard pattern, e.g. '*.log' or 'report_*.txt'.

    Yields:
        Path objects for each matching file.

    Hint: Use path.rglob('*') to get all files, then use
    fnmatch.fnmatch(path.name, pattern) to test if the filename matches.
    Note: rglob() itself supports patterns too — try path.rglob(pattern)
    as a simpler alternative!
    """
    root = Path(directory)

    # TODO: Check if the directory exists. If not, print an error and return.
    # Hint: use root.exists() and root.is_dir()

    # APPROACH A (using rglob with the pattern directly — simpler):
    # TODO: Use root.rglob(pattern) and yield each result that is a file.

    # APPROACH B (using fnmatch — more flexible, teaches fnmatch module):
    # TODO: Use root.rglob('*') to iterate everything, then check
    # fnmatch.fnmatch(entry.name, pattern) to filter matching files.

    pass  # Remove this and add your code


def format_size(size_bytes: int) -> str:
    """Return a human-readable size string like '1.2 KB' or '3.4 MB'."""
    # TODO: Convert bytes to KB or MB.
    # Hint: 1 KB = 1024 bytes, 1 MB = 1024 * 1024 bytes.
    # Return a string like '2.1 KB' or '0.5 MB'.
    pass


def print_results(directory: str, pattern: str, matches: list) -> None:
    """Print the search results."""
    print(f"\n  Searching for '{pattern}' in {directory}")
    print("  " + "─" * 55)

    if not matches:
        print(f"  No files found matching '{pattern}'.\n")
        return

    print(f"  Found {len(matches)} match(es):\n")
    for path in matches:
        size = format_size(path.stat().st_size)
        # TODO: Print each match with its size, formatted nicely.
        # Hint: use path.relative_to(directory) to show a shorter path,
        # or just use str(path) for the full path.
        pass

    print()


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python exercise.py <pattern> [directory]")
        print("Example: python exercise.py '*.py' .")
        sys.exit(1)

    search_pattern = sys.argv[1]
    search_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    # TODO: Call find_files() and collect results into a list.
    # TODO: Call print_results() with the list.
    pass


# ── HINTS ─────────────────────────────────────────────────────────────────────
# 1. rglob(pattern) is equivalent to rglob('*') filtered by fnmatch.
# 2. A generator function uses `yield` instead of `return`.
#    You can convert a generator to a list with list(my_generator()).
# 3. path.stat().st_size gives the file size in bytes.
# 4. path.relative_to(base) strips the base directory from the path.
