"""
Exercise 03 — Disk Space Alert
================================
GOAL: Write a script that checks disk usage on one or more mount points
and prints a warning (or exits with a non-zero code) when usage exceeds
a configurable threshold.

Expected output example:
    Disk Space Check  (threshold: 80%)
    ─────────────────────────────────────────────
    ✅  /           45.2%   (free: 234.1 GB)
    ⚠️   /var        82.1%   (free:   4.3 GB)  ← ABOVE THRESHOLD
    ✅  /tmp         12.0%   (free:  18.9 GB)

    1 partition(s) above threshold.
    Exit code 1 → use this in a cron job to trigger alerts!

CONCEPTS YOU WILL PRACTISE:
  - psutil.disk_usage()    — reading disk stats
  - Conditional logic      — if/elif/else
  - sys.exit()             — returning meaningful exit codes
  - String formatting      — aligned columns, colour output

HOW TO RUN:
    python exercise.py
    python exercise.py --threshold 50
    python exercise.py --mounts / /tmp
    echo $?   (check the exit code after running)
"""

import sys


# Colour helpers — these are ANSI escape codes for terminal colours.
# You don't need to change these; just call green("text") etc.
def green(s):
    return f"\033[92m{s}\033[0m"


def yellow(s):
    return f"\033[93m{s}\033[0m"


def red(s):
    return f"\033[91m{s}\033[0m"


def check_disk(mount: str, threshold: float) -> dict:
    """Check disk usage for a single mount point.

    Args:
        mount:     Mount point path, e.g. '/' or '/var'.
        threshold: Alert percentage (e.g. 80.0 means alert above 80%).

    Returns:
        A dict with keys: mount, total_gb, used_gb, free_gb, percent, alert.
        'alert' should be True if percent > threshold.

    Hint: psutil.disk_usage(mount) returns an object with:
        .total, .used, .free (in bytes) and .percent (0–100 float).
    """
    # TODO: Call psutil.disk_usage(mount) — wrap in try/except PermissionError.
    # TODO: Convert bytes to GB (divide by 1_073_741_824).
    # TODO: Return a dict with the required keys.
    pass


def print_report(results: list, threshold: float) -> int:
    """Print the disk usage report and return an exit code.

    Args:
        results:   List of dicts from check_disk().
        threshold: The threshold percentage used.

    Returns:
        0 if all partitions are below threshold, 1 if any are above.
    """
    print(f"\n  Disk Space Check  (threshold: {threshold:.0f}%)")
    print("  " + "─" * 55)

    alerts = 0
    for r in results:
        if r is None:
            continue

        pct = r["percent"]

        # TODO: Choose an icon and colour based on the usage level:
        #   Below threshold     → green ✅
        #   Above threshold     → red   ❌  (increment `alerts`)
        # Hint: Use the colour helper functions defined above.
        icon = "?"  # Replace with your logic
        pct_str = f"{pct:.1f}%"  # TODO: wrap in a colour function

        alert_tag = "  ← ABOVE THRESHOLD" if r["alert"] else ""
        print(f"  {icon}  {r['mount']:<15} {pct_str:<8} (free: {r['free_gb']:>6.1f} GB){alert_tag}")

    print()
    if alerts:
        print(red(f"  {alerts} partition(s) above {threshold:.0f}% threshold."))
    else:
        print(green("  All partitions within safe limits."))
    print()

    # TODO: Return 1 if there were any alerts, 0 otherwise.
    return 0  # Replace with your logic


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Check disk space thresholds.")
    parser.add_argument(
        "--threshold", type=float, default=80.0, help="Alert threshold in percent (default: 80)"
    )
    parser.add_argument(
        "--mounts", nargs="+", default=None, help="Mount points to check (default: all partitions)"
    )
    args = parser.parse_args()

    # TODO: Build the list of mount points to check.
    # If args.mounts is None, use psutil.disk_partitions() to get all mounts.
    # Hint: [p.mountpoint for p in psutil.disk_partitions()]
    mounts = []  # Replace with your logic

    # TODO: Call check_disk() for each mount and collect results.
    results = []  # Replace with your logic

    exit_code = print_report(results, args.threshold)
    sys.exit(exit_code)


# ── HINTS ─────────────────────────────────────────────────────────────────────
# 1. psutil.disk_usage('/') returns a named tuple — access fields by name.
# 2. sys.exit(1) exits with error code 1 — cron jobs and shell scripts can
#    detect this with `if [ $? -ne 0 ]; then send_alert; fi`.
# 3. Try running: python exercise.py --threshold 1
#    to see the alert trigger for almost every partition.
