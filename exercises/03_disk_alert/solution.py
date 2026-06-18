"""
Exercise 03 — Disk Space Alert  ✅ SOLUTION
"""

from __future__ import annotations

import sys

import psutil


def green(s):
    return f"\033[92m{s}\033[0m"


def red(s):
    return f"\033[91m{s}\033[0m"


def check_disk(mount: str, threshold: float) -> dict | None:
    try:
        usage = psutil.disk_usage(mount)
    except PermissionError:
        return None
    return {
        "mount": mount,
        "total_gb": usage.total / 1_073_741_824,
        "used_gb": usage.used / 1_073_741_824,
        "free_gb": usage.free / 1_073_741_824,
        "percent": usage.percent,
        "alert": usage.percent > threshold,
    }


def print_report(results: list, threshold: float) -> int:
    print(f"\n  Disk Space Check  (threshold: {threshold:.0f}%)")
    print("  " + "─" * 55)

    alerts = 0
    for r in results:
        if r is None:
            continue
        pct = r["percent"]
        if r["alert"]:
            alerts += 1
            icon, pct_str = "❌", red(f"{pct:.1f}%")
        else:
            icon, pct_str = "✅", green(f"{pct:.1f}%")

        tag = "  ← ABOVE THRESHOLD" if r["alert"] else ""
        print(f"  {icon}  {r['mount']:<15} {pct_str:<20} (free: {r['free_gb']:>6.1f} GB){tag}")

    print()
    if alerts:
        print(red(f"  {alerts} partition(s) above {threshold:.0f}% threshold."))
    else:
        print(green("  All partitions within safe limits."))
    print()
    return 1 if alerts else 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=80.0)
    parser.add_argument("--mounts", nargs="+", default=None)
    args = parser.parse_args()

    mounts = args.mounts or [p.mountpoint for p in psutil.disk_partitions()]
    results = [check_disk(m, args.threshold) for m in mounts]
    sys.exit(print_report(results, args.threshold))
