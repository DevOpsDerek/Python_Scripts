"""
tail_log.py — Watch a log file in real time (like `tail -f`)
=============================================================
Concepts covered:
  - File seek/tell  (tracking position in a file)
  - time.sleep()    (polling loop)
  - KeyboardInterrupt (graceful Ctrl+C exit)
  - ANSI codes      (colour-coded log levels)
  - String methods  (line parsing, contains checks)
"""

import sys
import time
from pathlib import Path

# Colour map for known log level keywords
LEVEL_COLOURS = {
    "ERROR":    "\033[91m",   # Red
    "CRITICAL": "\033[91m",
    "FATAL":    "\033[91m",
    "WARNING":  "\033[93m",   # Yellow
    "WARN":     "\033[93m",
    "INFO":     "\033[94m",   # Blue
    "DEBUG":    "\033[90m",   # Dark grey
}
RESET = "\033[0m"


def colorize_line(line: str) -> str:
    """Apply colour to a log line based on its severity keyword.

    Checks each known level keyword; returns the coloured line or the
    original if no keyword is found.
    """
    upper = line.upper()
    for keyword, colour in LEVEL_COLOURS.items():
        if keyword in upper:
            return f"{colour}{line}{RESET}"
    return line


def tail_file(path: str, lines: int = 20, follow: bool = True, interval: float = 0.5) -> None:
    """Display the end of a file and optionally follow it for new content.

    Args:
        path:     Path to the log file.
        lines:    Number of existing lines to show on startup.
        follow:   If True, keep watching the file for new lines.
        interval: How often to check for new lines, in seconds.
    """
    file_path = Path(path)
    if not file_path.exists():
        print(f"  ❌ File not found: {file_path}")
        sys.exit(1)

    print(f"\n  📜 Tailing: {file_path}")
    if follow:
        print("  (Press Ctrl+C to stop)\n")

    with open(file_path, encoding="utf-8", errors="replace") as f:
        # --- Show last N lines on startup ---
        # Strategy: read all lines into a circular buffer of size N
        # This avoids loading the whole file into memory for the initial display.
        buffer = []
        for line in f:
            buffer.append(line.rstrip())
            if len(buffer) > lines:
                buffer.pop(0)  # Remove oldest line (FIFO)

        for line in buffer:
            print("  " + colorize_line(line))

        if not follow:
            return

        # --- Follow mode: poll for new lines ---
        print(f"\n  {'─' * 55}  watching…\n")
        try:
            while True:
                new_lines = f.readlines()  # Read any new content since last read
                for line in new_lines:
                    print("  " + colorize_line(line.rstrip()))

                if not new_lines:
                    time.sleep(interval)  # Nothing new — wait before checking again
                else:
                    sys.stdout.flush()    # Ensure output is written immediately

        except KeyboardInterrupt:
            print(f"\n\n  Stopped watching {file_path}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Watch a log file in real time.")
    parser.add_argument("file", help="Path to the log file to watch")
    parser.add_argument("-n", "--lines", type=int, default=20, help="Initial lines to show (default: 20)")
    parser.add_argument("-f", "--follow", action="store_true", default=True,
                        help="Follow the file for new lines (default: True)")
    parser.add_argument("--no-follow", dest="follow", action="store_false",
                        help="Print last N lines and exit")
    parser.add_argument("-i", "--interval", type=float, default=0.5, help="Poll interval in seconds (default: 0.5)")
    args = parser.parse_args()

    tail_file(args.file, lines=args.lines, follow=args.follow, interval=args.interval)

# ---------------------------------------------------------------------------
# TRY THIS:
#   python tail_log.py /var/log/system.log               # macOS
#   python tail_log.py /var/log/syslog                   # Linux
#   python tail_log.py myapp.log -n 50                   # last 50 lines
#   python tail_log.py myapp.log --no-follow             # just print, don't watch
# ---------------------------------------------------------------------------
