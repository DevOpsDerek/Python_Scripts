"""
count_errors.py — Count and summarise errors in a log file
===========================================================
Concepts covered:
  - re module           (pattern matching and extraction)
  - collections.Counter (automatic frequency counting)
  - Sorting and slicing
  - Context managers    (with open())
  - String methods
"""

import re
from collections import Counter
from pathlib import Path

# Pre-compiled patterns — compile once, use many times
ERROR_PATTERN = re.compile(
    r"\b(ERROR|CRITICAL|FATAL|EXCEPTION|TRACEBACK|Traceback)\b",
    re.IGNORECASE,
)

# Captures "Error: <description>" or "Exception: <description>" messages
ERROR_MESSAGE_PATTERN = re.compile(
    r"\b(?:ERROR|Exception|Error)\s*:?\s*(.{10,80})",
    re.IGNORECASE,
)

# IP addresses in log lines
IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def count_errors(log_path: str, top_n: int = 20) -> None:
    """Count errors by type and surface the most frequent ones.

    Args:
        log_path: Path to the log file to analyse.
        top_n:    Number of top error messages to display.
    """
    path = Path(log_path)
    if not path.exists():
        print(f"  ❌ File not found: {log_path}")
        return

    error_lines = 0  # Total lines containing an error keyword
    total_lines = 0  # Total lines in file
    level_counter = Counter()  # {level: count}
    message_counter = Counter()  # {error_message_snippet: count}
    hourly_errors: Counter = Counter()  # {hour: count}

    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            total_lines += 1
            line = line.rstrip()

            # Check for any error-level keyword
            match = ERROR_PATTERN.search(line)
            if not match:
                continue

            error_lines += 1
            level = match.group(1).upper()
            level_counter[level] += 1

            # Try to extract the error message text
            msg_match = ERROR_MESSAGE_PATTERN.search(line)
            if msg_match:
                msg = msg_match.group(1).strip()
                # Strip dynamic parts: numbers, UUIDs, paths — keeps grouping meaningful
                msg_clean = re.sub(r"\b\d+\b", "N", msg)  # Replace numbers with N
                msg_clean = re.sub(r"[0-9a-f]{8}-[0-9a-f-]+", "UUID", msg_clean)  # UUIDs
                msg_clean = re.sub(r"/\S+", "/PATH", msg_clean)  # File paths
                message_counter[msg_clean[:80]] += 1

            # Try to extract hour from common timestamp formats
            hour_match = re.search(r"\b(\d{2}):\d{2}:\d{2}\b", line)
            if hour_match:
                hourly_errors[hour_match.group(1)] += 1

    # --- Report ---
    error_pct = (error_lines / total_lines * 100) if total_lines else 0

    print(f"\n  🚨 ERROR SUMMARY: {path.name}")
    print(f"  {'─' * 55}")
    print(f"  Total lines:   {total_lines:>10,}")
    print(f"  Error lines:   {error_lines:>10,}  ({error_pct:.2f}%)")

    # --- Levels breakdown ---
    if level_counter:
        print("\n  BY LEVEL")
        print(f"  {'─' * 30}")
        for level, count in level_counter.most_common():
            pct = count / error_lines * 100 if error_lines else 0
            bar = "█" * min(int(pct / 2), 30)
            if level in ("ERROR", "CRITICAL", "FATAL"):
                colour = "\033[91m"
            else:
                colour = "\033[93m"
            print(f"  {colour}{level:<12}\033[0m {count:>8,}  ({pct:5.1f}%)  {bar}")

    # --- Top error messages ---
    if message_counter:
        print(f"\n  TOP {top_n} ERROR MESSAGES")
        print(f"  {'─' * 55}")
        for msg, count in message_counter.most_common(top_n):
            print(f"  {count:>6,}×  {msg}")

    # --- Errors by hour ---
    if hourly_errors:
        print("\n  ERRORS BY HOUR (UTC)")
        print(f"  {'─' * 40}")
        max_count = max(hourly_errors.values())
        for hour in sorted(hourly_errors.keys()):
            count = hourly_errors[hour]
            bar_len = int(count / max_count * 30) if max_count else 0
            bar = "█" * bar_len
            print(f"  {hour}:00  {count:>6,}  {bar}")

    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Count and summarise errors in a log file.")
    parser.add_argument("logfile", help="Path to the log file")
    parser.add_argument(
        "-n", "--top", type=int, default=20, help="Top N error messages (default: 20)"
    )
    args = parser.parse_args()

    count_errors(args.logfile, top_n=args.top)

# ---------------------------------------------------------------------------
# TRY THIS:
#   python count_errors.py /var/log/system.log
#   python count_errors.py myapp.log -n 5
# ---------------------------------------------------------------------------
