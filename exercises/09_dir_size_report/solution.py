"""
Exercise 09 — Directory Size Report  ✅ SOLUTION
"""

import os
from pathlib import Path


def get_dir_size(directory: Path) -> tuple:
    total_bytes = 0
    file_count = 0
    for dirpath, _, filenames in os.walk(directory):
        for fname in filenames:
            try:
                total_bytes += os.path.getsize(os.path.join(dirpath, fname))
                file_count += 1
            except (OSError, PermissionError):
                continue
    return total_bytes, file_count


def bytes_to_human(b: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


def report(directory: str, top_n: int) -> None:
    root = Path(directory)
    if not root.is_dir():
        print(f"  ❌ Not a directory: {root}")
        return

    print(f"\n  Scanning {root}  (this may take a moment…)")

    entries = []
    for child in root.iterdir():
        if child.is_dir():
            size_bytes, file_count = get_dir_size(child)
            entries.append({"name": child.name, "size_bytes": size_bytes, "file_count": file_count})

    entries.sort(key=lambda e: e["size_bytes"], reverse=True)
    if top_n:
        entries = entries[:top_n]

    print(f"\n  Directory Size Report: {root}")
    print("  " + "─" * 60)
    print(f"  {'Rank':<6} {'Size':>10}  {'Files':>8}   Directory")
    print("  " + "─" * 60)

    for rank, entry in enumerate(entries, start=1):
        print(f"  {rank:<6} {bytes_to_human(entry['size_bytes']):>10}  {entry['file_count']:>8,}   {entry['name']}")

    total_bytes = sum(e["size_bytes"] for e in entries)
    total_files = sum(e["file_count"] for e in entries)
    print("  " + "─" * 60)
    print(f"  Total: {bytes_to_human(total_bytes)} across {len(entries)} "
          f"director{'y' if len(entries) == 1 else 'ies'} ({total_files:,} files)\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?", default=".")
    parser.add_argument("--top", type=int, default=0)
    args = parser.parse_args()
    report(args.directory, args.top)
