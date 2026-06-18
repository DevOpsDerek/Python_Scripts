"""
Exercise 07 — Uptime Logger  ✅ SOLUTION
"""

import csv
import time
from datetime import datetime
from pathlib import Path

import psutil


def collect_sample() -> dict:
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_pct":   psutil.cpu_percent(interval=1),
        "mem_pct":   psutil.virtual_memory().percent,
        "disk_pct":  psutil.disk_usage("/").percent,
    }


def write_sample(output_file: str, sample: dict, write_header: bool) -> None:
    with open(output_file, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["timestamp", "cpu_pct", "mem_pct", "disk_pct"])
        writer.writerow([sample["timestamp"], sample["cpu_pct"],
                         sample["mem_pct"], sample["disk_pct"]])


def run_logger(output_file: str, interval: float, max_samples: int) -> None:
    path = Path(output_file)
    needs_header = not path.exists() or path.stat().st_size == 0

    print(f"\n  📊 Uptime Logger  →  {output_file}")
    print(f"  Interval: {interval}s  |  Max samples: {max_samples if max_samples else '∞'}")
    print("  Press Ctrl+C to stop.\n")
    print(f"  {'Timestamp':<22} {'CPU%':>6}  {'MEM%':>6}  {'DISK%':>6}")
    print("  " + "─" * 45)

    samples = 0
    try:
        while True:
            s = collect_sample()
            write_sample(output_file, s, needs_header)
            needs_header = False
            print(f"  {s['timestamp']:<22} {s['cpu_pct']:>6.1f}  {s['mem_pct']:>6.1f}  {s['disk_pct']:>6.1f}")
            samples += 1
            if max_samples and samples >= max_samples:
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        pass

    print(f"\n\n  Stopped. {samples} sample(s) written to {output_file}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", default="stats.csv")
    parser.add_argument("-i", "--interval", type=float, default=5.0)
    parser.add_argument("-n", "--max-samples", type=int, default=0)
    args = parser.parse_args()
    run_logger(args.output, args.interval, args.max_samples)
