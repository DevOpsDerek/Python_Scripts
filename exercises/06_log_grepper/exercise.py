"""
Exercise 06 — Log Grepper
===========================
GOAL: Write a script that searches one or more log files (or an entire
directory of logs) for lines matching a regex pattern, similar to `grep`.

Expected output example:
    Searching for 'ERROR' in /var/log/
    ─────────────────────────────────────────────────
    /var/log/syslog          line  423: Jun 18 10:01:02 host ERROR: disk full
    /var/log/app.log         line 1204: 2024-06-18 ERROR Failed to connect
    /var/log/app.log         line 1892: 2024-06-18 ERROR Timeout after 30s
    ─────────────────────────────────────────────────
    Found 3 match(es) across 2 file(s).

CONCEPTS YOU WILL PRACTISE:
  - re.search()            — regex pattern matching on a line
  - os.walk() / rglob()    — scanning directories for log files
  - Generator functions    — yielding matches one at a time
  - enumerate()            — getting line numbers while iterating

HOW TO RUN:
    python exercise.py ERROR /var/log/syslog
    python exercise.py "Failed|Error" /var/log/
    python exercise.py "timeout" . --ext .log --ext .txt
"""

import re
from pathlib import Path


def find_log_files(path: str, extensions: list) -> list:
    """Return a list of log file paths under *path*.

    If *path* is a file, return [path].
    If *path* is a directory, return all files with matching extensions.

    Args:
        path:       File or directory path.
        extensions: List of extensions to include, e.g. ['.log', '.txt'].
                    If empty, include ALL files.

    Returns:
        List of Path objects.

    Hint: Use Path(path).is_file() to distinguish files from directories.
    For directories, use rglob('*') and check path.suffix.
    """
    # TODO: Handle the single-file case.
    # TODO: Handle the directory case — walk the directory, filter by extension.
    pass


def grep_file(filepath: Path, pattern: str, ignore_case: bool):
    """Yield (line_number, line) tuples for lines matching *pattern*.

    This is a generator — it yields one match at a time.

    Args:
        filepath:    Path to the file to search.
        pattern:     Regex pattern string.
        ignore_case: If True, match case-insensitively.

    Yields:
        (line_number: int, line: str) tuples for matching lines.

    Hint: Use re.search(pattern, line, flags) to test each line.
    Use re.IGNORECASE as the flag for case-insensitive matching.
    Use enumerate(file, start=1) to get 1-based line numbers.
    """
    flags = re.IGNORECASE if ignore_case else 0
    # TODO: Open the file (use encoding='utf-8', errors='replace').
    # TODO: Use enumerate(f, start=1) to iterate with line numbers.
    # TODO: Use re.search(pattern, line, flags) to test each line.
    # TODO: Yield (line_number, line.rstrip()) for each match.
    pass


def search(path: str, pattern: str, extensions: list, ignore_case: bool) -> None:
    """Search all matching files and print results.

    Args:
        path:        File or directory to search.
        pattern:     Regex pattern.
        extensions:  File extensions to include.
        ignore_case: Case-insensitive matching flag.
    """
    log_files = find_log_files(path, extensions)

    if not log_files:
        print(f"\n  No files found to search in: {path}\n")
        return

    total_matches = 0
    matched_files = 0

    print(f"\n  Searching for '{pattern}' in {path}")
    print("  " + "─" * 60)

    for filepath in log_files:
        file_matches = 0
        try:
            for line_no, line in grep_file(filepath, pattern, ignore_case):
                # TODO: Print a match line showing filepath, line number, and content.
                # Hint: truncate long lines at 120 characters.
                # Format: f"  {filepath.name:<30} line {line_no:>5}: {line[:120]}"
                total_matches += 1
                file_matches += 1
        except (PermissionError, IsADirectoryError):
            continue

        if file_matches:
            matched_files += 1

    print("  " + "─" * 60)
    if total_matches:
        print(f"  Found {total_matches} match(es) across {matched_files} file(s).\n")
    else:
        print("  No matches found.\n")


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Search log files for a regex pattern.")
    parser.add_argument("pattern", help="Regex pattern to search for")
    parser.add_argument("path", help="File or directory to search")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="Case-insensitive search")
    parser.add_argument("--ext", action="append", default=[".log", ".txt"],
                        help="File extension to include (can repeat: --ext .log --ext .out)")
    args = parser.parse_args()

    search(args.path, args.pattern, args.ext, args.ignore_case)


# ── HINTS ─────────────────────────────────────────────────────────────────────
# 1. re.search(pattern, string) returns a match object (truthy) or None (falsy).
# 2. re.IGNORECASE (or re.I) makes the match case-insensitive.
# 3. enumerate(iterable, start=1) yields (1, item1), (2, item2), ...
# 4. EXTENSION: Highlight the matched portion in the output using
#    re.sub(pattern, '\033[93m\\g<0>\033[0m', line) to add yellow colour.
