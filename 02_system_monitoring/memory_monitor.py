"""
memory_monitor.py — Memory usage overview: RAM and swap
=======================================================
Concepts covered:
  - psutil.virtual_memory() and psutil.swap_memory()
  - Named tuples (the objects psutil returns)
  - Formatted table output
  - Identifying the top memory-consuming processes
"""

import psutil  # pip install psutil


def bytes_to_human(b: int) -> str:
    """Convert a byte count to a human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


def render_bar(percent: float, width: int = 35) -> str:
    """Render a usage bar with colour based on percentage."""
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)

    if percent < 70:
        colour = "\033[92m"  # Green
    elif percent < 90:
        colour = "\033[93m"  # Yellow
    else:
        colour = "\033[91m"  # Red

    return f"{colour}[{bar}]\033[0m {percent:.1f}%"


def show_memory() -> None:
    """Print a detailed memory usage report."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    print("\n  💾 MEMORY REPORT\n")
    print("  ─" * 35)

    # virtual_memory() returns a named tuple — you access fields by name
    print(f"  {'RAM Total':<20} {bytes_to_human(mem.total):>10}")
    print(f"  {'RAM Used':<20} {bytes_to_human(mem.used):>10}")
    print(f"  {'RAM Available':<20} {bytes_to_human(mem.available):>10}")
    print(f"  {'RAM Cached':<20} {bytes_to_human(getattr(mem, 'cached', 0)):>10}")  # Linux only
    print(f"  {'RAM Buffers':<20} {bytes_to_human(getattr(mem, 'buffers', 0)):>10}")  # Linux only
    print(f"\n  Usage: {render_bar(mem.percent)}")

    print("\n  ─" * 35)
    if swap.total > 0:
        print(f"  {'Swap Total':<20} {bytes_to_human(swap.total):>10}")
        print(f"  {'Swap Used':<20} {bytes_to_human(swap.used):>10}")
        print(f"  {'Swap Free':<20} {bytes_to_human(swap.free):>10}")
        print(f"\n  Swap: {render_bar(swap.percent)}")
    else:
        print("  Swap: not configured")


def show_top_memory_processes(top_n: int = 15) -> None:
    """List the processes consuming the most RAM.

    Args:
        top_n: How many processes to show.
    """
    print(f"\n\n  🔝 TOP {top_n} PROCESSES BY MEMORY\n")
    print(f"  {'PID':<8} {'RSS':>8} {'%MEM':>6}  {'Name'}")
    print("  " + "─" * 50)

    # Collect (rss, pid, name) tuples for all accessible processes
    procs = []
    for proc in psutil.process_iter(["pid", "name", "memory_info", "memory_percent"]):
        try:
            info = proc.info  # The dict we asked for in attrs above
            rss = info["memory_info"].rss if info["memory_info"] else 0
            procs.append((rss, info["pid"], info["name"], info["memory_percent"]))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Processes can disappear or be inaccessible — skip them
            continue

    # Sort by RSS (resident set size) descending
    procs.sort(reverse=True)

    for rss, pid, name, pct in procs[:top_n]:
        pct_str = f"{pct:.2f}" if pct else "0.00"
        print(f"  {pid:<8} {bytes_to_human(rss):>8} {pct_str:>6}%  {name}")

    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Show memory usage and top processes.")
    parser.add_argument(
        "-n", "--top", type=int, default=15, help="Number of top processes (default: 15)"
    )
    args = parser.parse_args()

    show_memory()
    show_top_memory_processes(top_n=args.top)

# ---------------------------------------------------------------------------
# TRY THIS:
#   python memory_monitor.py
#   python memory_monitor.py -n 5    # show only top 5 processes
# ---------------------------------------------------------------------------
