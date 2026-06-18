"""
Exercise 04 — Process Watchdog
================================
GOAL: Write a script that watches for a named process and alerts when
it is NOT running. Run it on a loop with a configurable check interval.

Expected output example:
    👀 Watching for process: 'nginx'  (check every 5s, Ctrl+C to stop)
    ─────────────────────────────────────────────────────────────────
    [10:23:01]  ✅  nginx is running  (PID 1234)
    [10:23:06]  ✅  nginx is running  (PID 1234)
    [10:23:11]  ❌  nginx is NOT running!  ← alert here
    [10:23:16]  ❌  nginx is NOT running!

CONCEPTS YOU WILL PRACTISE:
  - psutil.process_iter()   — iterating running processes
  - while True loop         — indefinite polling
  - time.sleep()            — interval between checks
  - datetime.now()          — timestamping each check
  - KeyboardInterrupt       — graceful Ctrl+C exit

HOW TO RUN:
    python exercise.py python          (watch for any python process)
    python exercise.py nginx -i 10    (check every 10 seconds)
"""


def is_process_running(name: str) -> tuple:
    """Check if at least one process with *name* is running.

    Args:
        name: Process name to search for (case-insensitive substring match).

    Returns:
        A tuple (is_running: bool, pid: int | None).
        If found, pid is the PID of the first match. Otherwise pid is None.

    Hint: Iterate with psutil.process_iter(['pid', 'name']).
    Use a try/except for psutil.NoSuchProcess and psutil.AccessDenied.
    """
    # TODO: Loop through psutil.process_iter(['pid', 'name']).
    # TODO: Check if `name` is a case-insensitive substring of proc.info['name'].
    # TODO: If found, return (True, proc.info['pid']).
    # TODO: If the loop finishes with no match, return (False, None).
    pass


def watch(process_name: str, interval: float) -> None:
    """Poll for the process every `interval` seconds until Ctrl+C.

    Args:
        process_name: Process name to monitor.
        interval:     Seconds between checks.
    """
    print(
        f"\n  👀 Watching for process: '{process_name}'  (check every {interval}s, Ctrl+C to stop)"
    )
    print("  " + "─" * 60)

    # TODO: Write a while True loop that:
    #   1. Gets the current timestamp with datetime.now().strftime(...)
    #   2. Calls is_process_running(process_name)
    #   3. Prints a timestamped ✅ or ❌ line based on the result
    #   4. Sleeps for `interval` seconds
    # TODO: Wrap the loop in a try/except KeyboardInterrupt to exit cleanly.
    pass


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Watch for a running process.")
    parser.add_argument("process", help="Process name to watch (e.g. python, nginx)")
    parser.add_argument(
        "-i", "--interval", type=float, default=5.0, help="Check interval in seconds (default: 5)"
    )
    args = parser.parse_args()

    # TODO: Call watch() with the parsed arguments.
    pass


# ── HINTS ─────────────────────────────────────────────────────────────────────
# 1. psutil.process_iter(['name', 'pid']) is more efficient than fetching all attrs.
# 2. datetime.now().strftime('%H:%M:%S') formats the time as HH:MM:SS.
# 3. Try: python exercise.py python -i 2
#    Open a second terminal, start/stop a python script, and watch the output.
# 4. EXTENSION CHALLENGE: Track how many consecutive failures have occurred
#    and only alert after 3 consecutive failures (to avoid flapping alerts).
