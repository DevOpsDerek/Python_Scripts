"""
find_duplicates.py — Find duplicate files by comparing their content
====================================================================
Concepts covered:
  - hashlib        (computing MD5/SHA256 checksums)
  - collections.defaultdict (grouping items by a key)
  - os.walk()      (recursive directory traversal)
  - File I/O       (reading files in binary mode)
  - Dictionary comprehensions
"""

import hashlib
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


def hash_file(path: Path, chunk_size: int = 65536) -> str:
    """Compute the SHA-256 hash of a file's contents.

    Reading in chunks means we never load the entire file into memory —
    important for large files.

    Args:
        path:       File to hash.
        chunk_size: How many bytes to read at a time (64 KB default).

    Returns:
        Hex digest string like '3b4c...'.
    """
    hasher = hashlib.sha256()  # Create a new SHA-256 hashing object

    with open(path, "rb") as f:  # "rb" = read binary (works for any file type)
        while chunk := f.read(chunk_size):  # Walrus operator := assigns + tests
            hasher.update(chunk)  # Feed the chunk into the hasher

    return hasher.hexdigest()  # Return the final hex string


def find_duplicates(directory: str = ".") -> Dict[str, List[Path]]:
    """Scan a directory tree and group files with identical content.

    Strategy (two-pass for efficiency):
      1. Group files by size — files with different sizes can't be duplicates.
      2. For each size group with >1 file, compare hashes.

    Args:
        directory: Root directory to scan.

    Returns:
        Dict mapping hash → list of duplicate Paths. Only groups with 2+ files.
    """
    root = Path(directory).resolve()
    print(f"\n🔍 Scanning for duplicates in: {root}\n")

    # --- Pass 1: Group by size ---
    # defaultdict(list) automatically creates an empty list for new keys
    size_groups: Dict[int, List[Path]] = defaultdict(list)

    scanned = 0
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            file_path = Path(dirpath) / filename
            try:
                size = file_path.stat().st_size
                if size > 0:  # Skip empty files — they're all "equal" but uninteresting
                    size_groups[size].append(file_path)
                    scanned += 1
            except (OSError, PermissionError):
                continue

    print(f"   Pass 1 complete: {scanned:,} files scanned.")

    # Candidates are size groups where more than one file has that size
    candidates = [paths for paths in size_groups.values() if len(paths) > 1]
    candidate_count = sum(len(g) for g in candidates)
    print(f"   {candidate_count:,} files need hash comparison ({len(candidates)} size groups).\n")

    # --- Pass 2: Hash candidates ---
    hash_groups: Dict[str, List[Path]] = defaultdict(list)
    hashed = 0

    for group in candidates:
        for file_path in group:
            try:
                file_hash = hash_file(file_path)
                hash_groups[file_hash].append(file_path)
                hashed += 1
                # Print progress every 100 files
                if hashed % 100 == 0:
                    print(f"   Hashing… {hashed}/{candidate_count}", end="\r")
            except (OSError, PermissionError, IsADirectoryError):
                continue

    # Keep only the groups that actually have more than one file (real duplicates)
    duplicates = {h: paths for h, paths in hash_groups.items() if len(paths) > 1}
    return duplicates


def report_duplicates(duplicates: Dict[str, List[Path]]) -> None:
    """Print a human-readable report of duplicate files."""
    if not duplicates:
        print("✅ No duplicate files found!")
        return

    total_groups = len(duplicates)
    total_wasted = 0

    print(f"\n{'=' * 60}")
    print(f"  Found {total_groups} group{'s' if total_groups != 1 else ''} of duplicate files")
    print(f"{'=' * 60}\n")

    for i, (file_hash, paths) in enumerate(sorted(duplicates.items()), start=1):
        size = paths[0].stat().st_size
        wasted = size * (len(paths) - 1)  # Space that could be saved by removing copies
        total_wasted += wasted

        # Show size in human-readable form
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                size_str = f"{size:.1f} {unit}"
                break
            size /= 1024
        else:
            size_str = f"{size:.1f} TB"

        print(f"  Group {i}: {len(paths)} identical files ({size_str} each)")
        print(f"  Hash: {file_hash[:12]}…")
        for path in paths:
            print(f"    • {path}")
        print()

    # Summary
    for unit in ["B", "KB", "MB", "GB"]:
        if total_wasted < 1024:
            wasted_str = f"{total_wasted:.1f} {unit}"
            break
        total_wasted /= 1024
    else:
        wasted_str = f"{total_wasted:.1f} TB"

    print(f"{'=' * 60}")
    print(f"  Potential space savings: {wasted_str}")
    print(f"{'=' * 60}\n")
    print("  ℹ️  This script only reports duplicates — it does NOT delete anything.")
    print("     Review the list above before removing any files manually.\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Find duplicate files in a directory.")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to scan (default: current)")
    args = parser.parse_args()

    dupes = find_duplicates(args.directory)
    report_duplicates(dupes)

# ---------------------------------------------------------------------------
# TRY THIS:
#   python find_duplicates.py ~/Downloads
#   python find_duplicates.py ~/Pictures
# ---------------------------------------------------------------------------
