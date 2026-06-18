"""
find_process.py — Find processes by name or keyword and show their details
==========================================================================
Concepts covered:
  - psutil process inspection
  - List comprehensions with conditions
  - String methods: lower(), in, startswith()
  - psutil.Process() methods: connections(), open_files(), etc.
  - Pretty-printing nested data structures
"""

from datetime import datetime

import psutil  # pip install psutil


def format_bytes(b: int) -> str:
    """Human-readable file size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def find_processes(keyword: str) -> list:
    """Return a list of processes whose name or command line contains *keyword*.

    Args:
        keyword: Case-insensitive search string.

    Returns:
        List of psutil.Process objects that match.
    """
    matches = []
    kw = keyword.lower()

    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            name = (proc.info["name"] or "").lower()
            cmdline = " ".join(proc.info["cmdline"] or []).lower()

            if kw in name or kw in cmdline:
                matches.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return matches


def print_process_detail(proc: psutil.Process) -> None:
    """Print detailed information about a single process.

    Args:
        proc: A psutil.Process object.
    """
    try:
        # with proc.oneshot() batches multiple attribute reads into one syscall
        # — much more efficient than calling proc.name(), proc.cpu_percent(), etc. separately
        with proc.oneshot():
            print(f"\n  {'─' * 55}")
            print(f"  PID:        {proc.pid}")
            print(f"  Name:       {proc.name()}")
            print(f"  Status:     {proc.status()}")
            print(f"  User:       {proc.username()}")

            # Executable path
            try:
                print(f"  Exe:        {proc.exe()}")
            except (psutil.AccessDenied, FileNotFoundError):
                print("  Exe:        (access denied)")

            # Full command line arguments
            try:
                cmdline = " ".join(proc.cmdline())
                print(f"  Command:    {cmdline[:80]}{'…' if len(cmdline) > 80 else ''}")
            except psutil.AccessDenied:
                print("  Command:    (access denied)")

            # Start time and running duration
            start = datetime.fromtimestamp(proc.create_time())
            uptime = datetime.now() - start
            print(f"  Started:    {start.strftime('%Y-%m-%d %H:%M:%S')}  (running {uptime.seconds // 60}m)")

            # CPU and memory
            # NOTE: cpu_percent needs an interval or a prior call to be meaningful
            cpu_pct = proc.cpu_percent(interval=0.1)
            mem = proc.memory_info()
            print(f"  CPU:        {cpu_pct:.1f}%")
            print(f"  Memory:     RSS {format_bytes(mem.rss)}  /  VMS {format_bytes(mem.vms)}")

            # Threads
            print(f"  Threads:    {proc.num_threads()}")

            # Open files
            try:
                open_files = proc.open_files()
                if open_files:
                    print(f"  Open files: {len(open_files)}")
                    for f in open_files[:5]:  # Show first 5 to avoid flooding output
                        print(f"    • {f.path}")
                    if len(open_files) > 5:
                        print(f"    … and {len(open_files) - 5} more")
            except psutil.AccessDenied:
                print("  Open files: (access denied)")

            # Network connections
            try:
                conns = proc.connections()
                if conns:
                    print(f"  Connections: {len(conns)}")
                    for c in conns[:5]:
                        laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "-"
                        raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "-"
                        print(f"    • {c.type.name}  {laddr} → {raddr}  [{c.status}]")
            except psutil.AccessDenied:
                print("  Connections: (access denied)")

    except psutil.NoSuchProcess:
        print(f"  Process {proc.pid} no longer exists.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Find processes by name or keyword.")
    parser.add_argument("keyword", help="Search keyword (case-insensitive, checks name and cmdline)")
    parser.add_argument("-d", "--detail", action="store_true", help="Show full details for each match")
    args = parser.parse_args()

    print(f"\n  Searching for processes matching: '{args.keyword}'\n")
    matches = find_processes(args.keyword)

    if not matches:
        print(f"  No processes found matching '{args.keyword}'.\n")
    elif args.detail:
        print(f"  Found {len(matches)} process{'es' if len(matches) != 1 else ''}:\n")
        for proc in matches:
            print_process_detail(proc)
        print()
    else:
        print(f"  Found {len(matches)} process{'es' if len(matches) != 1 else ''}:\n")
        print(f"  {'PID':<8} {'Name':<25} {'Status':<12} {'User'}")
        print("  " + "─" * 60)
        for proc in matches:
            try:
                print(f"  {proc.pid:<8} {proc.name():<25} {proc.status():<12} {proc.username()}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        print("\n  Tip: Add --detail for full information per process.\n")

# ---------------------------------------------------------------------------
# TRY THIS:
#   python find_process.py python
#   python find_process.py python --detail
#   python find_process.py chrome
#   python find_process.py ssh
# ---------------------------------------------------------------------------
