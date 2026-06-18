"""
disk_usage.py — Visualise disk space usage across all mounted partitions
========================================================================
Concepts covered:
  - psutil.disk_partitions() and psutil.disk_usage()
  - Sorting with key functions
  - Terminal colour output with ANSI codes
  - Exception handling for permission-denied partitions
  - Named tuples (psutil returns these)
"""

import psutil  # pip install psutil


# ANSI colour helpers — wrap text in escape codes for terminal colour
def green(s: str) -> str:
    return f"\033[92m{s}\033[0m"


def yellow(s: str) -> str:
    return f"\033[93m{s}\033[0m"


def red(s: str) -> str:
    return f"\033[91m{s}\033[0m"


def bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def colorize_usage(percent: float, text: str) -> str:
    """Return *text* coloured based on how full the disk is."""
    if percent < 70:
        return green(text)
    elif percent < 90:
        return yellow(text)
    else:
        return red(text)


def render_bar(percent: float, width: int = 30) -> str:
    """Build a usage bar and colour it by fill level."""
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)
    return colorize_usage(percent, f"[{bar}]")


def bytes_to_human(b: int) -> str:
    """Convert bytes to human-readable units."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


def show_disk_usage(skip_virtual: bool = True) -> None:
    """Print a formatted disk-usage report for all mounted partitions.

    Args:
        skip_virtual: Skip pseudo-filesystems like tmpfs, devfs, etc.
    """
    # These filesystem types are usually virtual/proc/dev — not real storage
    VIRTUAL_FSTYPES = {
        "tmpfs",
        "devtmpfs",
        "devfs",
        "proc",
        "sysfs",
        "cgroup",
        "cgroup2",
        "overlay",
        "squashfs",
    }

    partitions = psutil.disk_partitions(all=False)  # all=False skips virtual mounts on Linux
    # Sort by mountpoint for consistent ordering
    partitions = sorted(partitions, key=lambda p: p.mountpoint)

    print(f"\n  {bold('DISK USAGE REPORT')}\n")
    print(f"  {'Mount':<20} {'Device':<20} {'FS':<8} {'Total':>8} {'Used':>8} {'Free':>8}  Usage")
    print("  " + "─" * 85)

    total_space = 0
    total_used = 0

    for part in partitions:
        # Skip virtual filesystems if requested
        if skip_virtual and part.fstype.lower() in VIRTUAL_FSTYPES:
            continue

        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            print(f"  {part.mountpoint:<20} {'(permission denied)'}")
            continue

        total_space += usage.total
        total_used += usage.used

        pct = usage.percent
        bar = render_bar(pct)
        pct_str = colorize_usage(pct, f"{pct:.1f}%")

        # Truncate long device paths for display
        device = part.device[-18:] if len(part.device) > 18 else part.device

        print(
            f"  {part.mountpoint:<20} {device:<20} {part.fstype:<8} "
            f"{bytes_to_human(usage.total):>8} "
            f"{bytes_to_human(usage.used):>8} "
            f"{bytes_to_human(usage.free):>8}  "
            f"{bar} {pct_str}"
        )

    # --- Summary ---
    if total_space:
        overall_pct = (total_used / total_space) * 100
        print("  " + "─" * 85)
        print(
            f"  {'TOTAL':<20} {'':<20} {'':<8} "
            f"{bytes_to_human(total_space):>8} "
            f"{bytes_to_human(total_used):>8} "
            f"{bytes_to_human(total_space - total_used):>8}  "
            f"{render_bar(overall_pct)} {colorize_usage(overall_pct, f'{overall_pct:.1f}%')}"
        )

    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Show disk usage for all partitions.")
    parser.add_argument("--all", action="store_true", help="Include virtual filesystems")
    args = parser.parse_args()

    show_disk_usage(skip_virtual=not args.all)

# ---------------------------------------------------------------------------
# TRY THIS:
#   python disk_usage.py
#   python disk_usage.py --all       # include virtual filesystems
# ---------------------------------------------------------------------------
