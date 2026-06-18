"""
parse_logs.py — Parse and analyse log files with regex and counters
====================================================================
Concepts covered:
  - re module      (regular expressions for pattern matching)
  - collections.Counter  (counting occurrences)
  - collections.defaultdict
  - File I/O       (reading large files line-by-line, memory-efficient)
  - datetime.strptime()  (parsing date strings)
  - Generator functions
"""

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Generator

# ---------------------------------------------------------------------------
# Log format patterns — we compile them once for efficiency.
# re.compile() pre-processes the pattern so repeated use is faster.
# ---------------------------------------------------------------------------

# Standard syslog format:  Jun 18 12:00:00 hostname service[pid]: message
SYSLOG_PATTERN = re.compile(
    r"^(?P<month>\w+)\s+(?P<day>\d+)\s+(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<host>\S+)\s+(?P<service>\S+?)(?:\[(?P<pid>\d+)\])?\s*:\s*(?P<message>.+)$"
)

# Apache/Nginx combined log format
APACHE_PATTERN = re.compile(
    r'(?P<ip>[\d.]+)\s+-\s+-\s+\[(?P<datetime>[^\]]+)\]\s+'
    r'"(?P<method>\w+)\s+(?P<path>\S+)\s+\S+"\s+'
    r'(?P<status>\d{3})\s+(?P<size>\d+|-)'
)

# Generic "level" detector — matches ERROR, WARNING, WARN, INFO, DEBUG, CRITICAL
LEVEL_PATTERN = re.compile(
    r"\b(ERROR|CRITICAL|WARNING|WARN|INFO|DEBUG|FATAL)\b",
    re.IGNORECASE
)


def iter_lines(path: str, encoding: str = "utf-8", errors: str = "replace") -> Generator[str, None, None]:
    """Yield lines from a file one at a time (memory-efficient for large logs).

    Args:
        path:     Path to the log file.
        encoding: File encoding (default: utf-8).
        errors:   How to handle decode errors ('replace' keeps going).

    Yields:
        Individual lines as strings (newline stripped).
    """
    with open(path, encoding=encoding, errors=errors) as f:
        for line in f:
            yield line.rstrip("\n")


def analyse_log(log_path: str) -> Dict[str, Any]:
    """Perform a statistical analysis of a log file.

    Args:
        log_path: Path to the log file to analyse.

    Returns:
        A dict of analysis results.
    """
    path = Path(log_path)
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {log_path}")

    stats: Dict[str, Any] = {
        "file": str(path),
        "size_bytes": path.stat().st_size,
        "total_lines": 0,
        "level_counts": Counter(),         # {level: count}
        "service_counts": Counter(),       # {service: count}  (syslog only)
        "ip_counts": Counter(),            # {ip: count}       (apache only)
        "status_counts": Counter(),        # {http_status: count}
        "errors": [],                      # First 20 error lines
        "hourly_counts": defaultdict(int), # {hour_string: count}
    }

    for line in iter_lines(log_path):
        stats["total_lines"] += 1

        # --- Detect log level ---
        level_match = LEVEL_PATTERN.search(line)
        if level_match:
            level = level_match.group(1).upper()
            # Normalise WARN → WARNING
            if level == "WARN":
                level = "WARNING"
            stats["level_counts"][level] += 1
            if level in ("ERROR", "CRITICAL", "FATAL") and len(stats["errors"]) < 20:
                stats["errors"].append(line[:200])  # Keep first 200 chars of each error

        # --- Syslog format? ---
        syslog_match = SYSLOG_PATTERN.match(line)
        if syslog_match:
            service = syslog_match.group("service").split("[")[0]
            stats["service_counts"][service] += 1
            hour = syslog_match.group("time")[:2]  # HH from HH:MM:SS
            stats["hourly_counts"][hour] += 1

        # --- Apache format? ---
        apache_match = APACHE_PATTERN.match(line)
        if apache_match:
            stats["ip_counts"][apache_match.group("ip")] += 1
            stats["status_counts"][apache_match.group("status")] += 1

    return stats


def print_report(stats: Dict[str, Any]) -> None:
    """Pretty-print the analysis results."""
    size_kb = stats["size_bytes"] / 1024
    print("\n  📋 LOG ANALYSIS REPORT")
    print(f"  {'─' * 55}")
    print(f"  File:        {stats['file']}")
    print(f"  Size:        {size_kb:.1f} KB")
    print(f"  Total lines: {stats['total_lines']:,}")

    # --- Log levels ---
    if stats["level_counts"]:
        print("\n  LOG LEVELS")
        print(f"  {'─' * 30}")
        for level, count in stats["level_counts"].most_common():
            bar = "█" * min(count, 40)
            colour = {
                "ERROR": "\033[91m", "CRITICAL": "\033[91m", "FATAL": "\033[91m",
                "WARNING": "\033[93m",
                "INFO": "\033[94m",
                "DEBUG": "\033[90m",
            }.get(level, "")
            reset = "\033[0m" if colour else ""
            print(f"  {colour}{level:<12}{reset} {count:>7,}  {bar}")

    # --- Top services (syslog) ---
    if stats["service_counts"]:
        print("\n  TOP SERVICES (syslog)")
        print(f"  {'─' * 30}")
        for svc, count in stats["service_counts"].most_common(10):
            print(f"  {svc:<25} {count:>7,}")

    # --- Top IPs (Apache) ---
    if stats["ip_counts"]:
        print("\n  TOP CLIENT IPs (Apache/Nginx)")
        print(f"  {'─' * 30}")
        for ip, count in stats["ip_counts"].most_common(10):
            print(f"  {ip:<20} {count:>7,} requests")

    # --- HTTP status codes ---
    if stats["status_counts"]:
        print("\n  HTTP STATUS CODES")
        print(f"  {'─' * 30}")
        for status, count in sorted(stats["status_counts"].items()):
            colour = "\033[91m" if status.startswith("5") else (
                     "\033[93m" if status.startswith("4") else "")
            reset = "\033[0m" if colour else ""
            print(f"  {colour}{status}{reset}   {count:>7,}")

    # --- Sample errors ---
    if stats["errors"]:
        print(f"\n  SAMPLE ERROR LINES (first {len(stats['errors'])})")
        print(f"  {'─' * 55}")
        for err in stats["errors"][:10]:
            print(f"  \033[91m{err[:100]}\033[0m")
        if len(stats["errors"]) > 10:
            print(f"  … and {len(stats['errors']) - 10} more")

    print()


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Analyse a log file.")
    parser.add_argument("logfile", help="Path to the log file")
    args = parser.parse_args()

    try:
        results = analyse_log(args.logfile)
        print_report(results)
    except FileNotFoundError as e:
        print(f"\n  ❌ {e}\n")
        sys.exit(1)

# ---------------------------------------------------------------------------
# TRY THIS:
#   python parse_logs.py /var/log/system.log         # macOS
#   python parse_logs.py /var/log/syslog             # Linux
#   python parse_logs.py /var/log/apache2/access.log # Apache
# ---------------------------------------------------------------------------
