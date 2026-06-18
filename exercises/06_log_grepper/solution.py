"""
Exercise 06 — Log Grepper  ✅ SOLUTION
"""

import re
from pathlib import Path


def find_log_files(path: str, extensions: list) -> list:
    p = Path(path)
    if p.is_file():
        return [p]
    if p.is_dir():
        files = [f for f in p.rglob("*") if f.is_file()]
        if extensions:
            files = [f for f in files if f.suffix.lower() in extensions]
        return sorted(files)
    return []


def grep_file(filepath: Path, pattern: str, ignore_case: bool):
    flags = re.IGNORECASE if ignore_case else 0
    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            for line_no, line in enumerate(f, start=1):
                if re.search(pattern, line, flags):
                    yield line_no, line.rstrip()
    except Exception:
        return


def search(path: str, pattern: str, extensions: list, ignore_case: bool) -> None:
    log_files = find_log_files(path, extensions)
    if not log_files:
        print(f"\n  No files found in: {path}\n")
        return

    total_matches = 0
    matched_files = 0

    print(f"\n  Searching for '{pattern}' in {path}")
    print("  " + "─" * 60)

    flags = re.IGNORECASE if ignore_case else 0

    def highlight(line: str) -> str:
        return re.sub(pattern, lambda m: f"\033[93m{m.group()}\033[0m", line, flags=flags)

    for filepath in log_files:
        file_matches = 0
        for line_no, line in grep_file(filepath, pattern, ignore_case):
            print(f"  {filepath.name:<30} line {line_no:>5}: {highlight(line[:120])}")
            total_matches += 1
            file_matches += 1
        if file_matches:
            matched_files += 1

    print("  " + "─" * 60)
    if total_matches:
        print(f"  Found {total_matches} match(es) across {matched_files} file(s).\n")
    else:
        print("  No matches found.\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("pattern")
    parser.add_argument("path")
    parser.add_argument("-i", "--ignore-case", action="store_true")
    parser.add_argument("--ext", action="append", default=[".log", ".txt"])
    args = parser.parse_args()
    search(args.path, args.pattern, args.ext, args.ignore_case)
