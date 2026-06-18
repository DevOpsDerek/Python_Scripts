"""
list_processes.py — Show all running processes in a sortable table
==================================================================
Concepts covered:
  - psutil.process_iter()  (iterate over all running processes)
  - Sorting with operator.attrgetter
  - Exception handling (psutil.NoSuchProcess, psutil.AccessDenied)
  - String formatting for tabular output
  - Command-line argument parsing with argparse
"""

from datetime import datetime

import psutil  # pip install psutil


def bytes_to_mb(b: int) -> float:
    """Convert bytes to megabytes."""
    return b / 1_048_576  # 1 MB = 1024 * 1024 bytes


def get_process_start(proc: psutil.Process) -> str:
    """Return the process start time as a readable string."""
    try:
        start_ts = proc.create_time()  # Unix timestamp
        return datetime.fromtimestamp(start_ts).strftime("%H:%M:%S")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return "N/A"


def list_processes(
    sort_by: str = "cpu",
    top_n: int = 30,
    filter_name: str = "",
) -> None:
    """Print a snapshot of running processes.

    Args:
        sort_by:     Sort field: 'cpu', 'mem', 'pid', or 'name'.
        top_n:       Maximum number of processes to display.
        filter_name: Only show processes whose name contains this string.
    """
    # Specify exactly which attributes we want — more efficient than fetching all
    attrs = [
        "pid",
        "name",
        "username",
        "status",
        "cpu_percent",
        "memory_info",
        "memory_percent",
        "create_time",
        "cmdline",
    ]

    processes = []

    for proc in psutil.process_iter(attrs):
        try:
            info = proc.info  # Dict of the requested attributes
            rss_mb = bytes_to_mb(info["memory_info"].rss) if info["memory_info"] else 0.0

            # Apply name filter if provided (case-insensitive substring match)
            if filter_name and filter_name.lower() not in (info["name"] or "").lower():
                continue

            processes.append(
                {
                    "pid": info["pid"],
                    "name": (info["name"] or "")[:25],
                    "user": (info["username"] or "")[:15],
                    "status": info["status"] or "",
                    "cpu": info["cpu_percent"] or 0.0,
                    "mem_mb": rss_mb,
                    "mem_pct": info["memory_percent"] or 0.0,
                    "started": datetime.fromtimestamp(info["create_time"]).strftime("%H:%M:%S")
                    if info["create_time"]
                    else "N/A",
                }
            )

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Processes can vanish or be off-limits — silently skip them
            continue

    # --- Sort ---
    SORT_KEYS = {
        "cpu": lambda p: p["cpu"],
        "mem": lambda p: p["mem_mb"],
        "pid": lambda p: p["pid"],
        "name": lambda p: p["name"].lower(),
    }
    key_fn = SORT_KEYS.get(sort_by, SORT_KEYS["cpu"])
    processes.sort(key=key_fn, reverse=(sort_by in ("cpu", "mem")))

    # --- Display ---
    print(
        f"\n  Running Processes  —  sorted by {sort_by.upper()}  (showing {min(top_n, len(processes))} of {len(processes)})\n"
    )
    print(
        f"  {'PID':<7} {'Name':<26} {'User':<16} {'Status':<10} {'CPU%':>6} {'RSS MB':>8} {'MEM%':>6}  Started"
    )
    print("  " + "─" * 95)

    for proc in processes[:top_n]:
        # Colour-code status for quick visual scanning
        status = proc["status"]
        if status == "running":
            status_str = f"\033[92m{status:<10}\033[0m"
        elif status == "sleeping":
            status_str = f"{status:<10}"
        else:
            status_str = f"\033[93m{status:<10}\033[0m"

        cpu_str = f"{proc['cpu']:>6.1f}"
        if proc["cpu"] > 50:
            cpu_str = f"\033[91m{cpu_str}\033[0m"  # Red if high CPU

        print(
            f"  {proc['pid']:<7} {proc['name']:<26} {proc['user']:<16} {status_str} "
            f"{cpu_str} {proc['mem_mb']:>8.1f} {proc['mem_pct']:>6.1f}%  {proc['started']}"
        )

    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="List running processes.")
    parser.add_argument(
        "-s",
        "--sort",
        choices=["cpu", "mem", "pid", "name"],
        default="cpu",
        help="Sort by: cpu, mem, pid, name (default: cpu)",
    )
    parser.add_argument(
        "-n", "--top", type=int, default=30, help="Max processes to show (default: 30)"
    )
    parser.add_argument("-f", "--filter", default="", help="Filter by process name substring")
    args = parser.parse_args()

    import time

    # First call to cpu_percent() always returns 0.0; call once to prime the counters
    psutil.cpu_percent(percpu=True)
    time.sleep(0.5)

    list_processes(sort_by=args.sort, top_n=args.top, filter_name=args.filter)

# ---------------------------------------------------------------------------
# TRY THIS:
#   python list_processes.py
#   python list_processes.py --sort mem
#   python list_processes.py --filter python
#   python list_processes.py -n 5 -s cpu
# ---------------------------------------------------------------------------
