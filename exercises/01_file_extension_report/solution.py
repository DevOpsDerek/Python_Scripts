"""
Exercise 01 — File Extension Report  ✅ SOLUTION
=================================================
Compare your approach to this solution — there is often more than one
correct way to solve a problem in Python!
"""

import sys
from collections import Counter
from pathlib import Path


def get_extension(path: Path) -> str:
    suffix = path.suffix.lower()
    return suffix if suffix else "(no ext)"


def count_extensions(directory: str) -> Counter:
    root = Path(directory)
    counts: Counter = Counter()
    for entry in root.rglob("*"):
        if entry.is_file():
            counts[get_extension(entry)] += 1
    return counts


def render_bar(count: int, max_count: int, width: int = 20) -> str:
    filled = int(count / max_count * width)
    return "█" * filled


def print_report(directory: str, counts: Counter) -> None:
    print(f"\n  File Extension Report: {directory}")
    print("  " + "─" * 50)

    if not counts:
        print("  No files found.")
        return

    max_count = counts.most_common(1)[0][1]

    for extension, count in counts.most_common():
        bar = render_bar(count, max_count)
        print(f"  {extension:<12} {count:>5} file{'s' if count != 1 else ' '}  {bar}")

    print(f"\n  Total: {sum(counts.values())} files across {len(counts)} extension(s)\n")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print_report(target, count_extensions(target))
