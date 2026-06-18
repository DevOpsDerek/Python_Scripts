"""
Exercise 02 — Find Files by Pattern  ✅ SOLUTION
"""

import sys
from pathlib import Path


def find_files(directory: str, pattern: str):
    root = Path(directory)
    if not root.exists() or not root.is_dir():
        print(f"  ❌ Directory not found: {root}")
        return
    yield from (f for f in root.rglob(pattern) if f.is_file())


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def print_results(directory: str, pattern: str, matches: list) -> None:
    print(f"\n  Searching for '{pattern}' in {directory}")
    print("  " + "─" * 55)

    if not matches:
        print(f"  No files found matching '{pattern}'.\n")
        return

    print(f"  Found {len(matches)} match(es):\n")
    for path in sorted(matches):
        size = format_size(path.stat().st_size)
        try:
            display = path.relative_to(directory)
        except ValueError:
            display = path
        print(f"  {str(display):<50} ({size})")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python solution.py <pattern> [directory]")
        sys.exit(1)

    search_pattern = sys.argv[1]
    search_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    results = list(find_files(search_dir, search_pattern))
    print_results(search_dir, search_pattern, results)
