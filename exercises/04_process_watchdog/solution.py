"""
Exercise 04 — Process Watchdog  ✅ SOLUTION
"""

import time
from datetime import datetime

import psutil


def is_process_running(name: str) -> tuple:
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if name.lower() in (proc.info["name"] or "").lower():
                return True, proc.info["pid"]
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False, None


def watch(process_name: str, interval: float) -> None:
    print(
        f"\n  👀 Watching for process: '{process_name}'  (check every {interval}s, Ctrl+C to stop)"
    )
    print("  " + "─" * 60)

    try:
        while True:
            ts = datetime.now().strftime("%H:%M:%S")
            running, pid = is_process_running(process_name)
            if running:
                print(f"  [{ts}]  \033[92m✅  {process_name} is running  (PID {pid})\033[0m")
            else:
                print(f"  [{ts}]  \033[91m❌  {process_name} is NOT running!\033[0m")
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n\n  Stopped watching '{process_name}'.\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("process")
    parser.add_argument("-i", "--interval", type=float, default=5.0)
    args = parser.parse_args()
    watch(args.process, args.interval)
