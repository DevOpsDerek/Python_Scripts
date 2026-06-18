"""
Exercise 07 — Uptime Logger
==============================
GOAL: Write a script that periodically samples CPU, memory, and disk usage,
and appends each sample as a row in a CSV file. The CSV can then be opened
in Excel/Numbers/Sheets for graphing.

Expected CSV output (stats.csv):
    timestamp,cpu_pct,mem_pct,disk_pct
    2024-06-18 10:00:00,12.3,45.1,67.2
    2024-06-18 10:00:05,14.7,45.3,67.2
    2024-06-18 10:00:10,9.1,45.0,67.2

CONCEPTS YOU WILL PRACTISE:
  - csv module             — writing CSV rows with csv.writer
  - File append mode       — open(path, 'a') adds to existing files
  - psutil                 — reading CPU/memory/disk stats
  - time.sleep()           — polling interval
  - datetime               — timestamping rows

HOW TO RUN:
    python exercise.py                        (5s interval, stats.csv)
    python exercise.py -i 1 -o my_stats.csv  (1s interval, custom file)
    python exercise.py -n 10                  (stop after 10 samples)
"""

from pathlib import Path


def collect_sample() -> dict:
    """Collect one system stats sample.

    Returns:
        A dict with keys: timestamp, cpu_pct, mem_pct, disk_pct.

    Hints:
      - datetime.now().strftime('%Y-%m-%d %H:%M:%S') for the timestamp.
      - psutil.cpu_percent(interval=1) for CPU (the interval=1 means it
        measures over 1 second — don't use 0 or it returns 0.0).
      - psutil.virtual_memory().percent for memory.
      - psutil.disk_usage('/').percent for disk.
    """
    # TODO: Get the current timestamp as a formatted string.
    # TODO: Get CPU, memory, and disk percentages using psutil.
    # TODO: Return a dict with the four keys.
    pass


def write_sample(output_file: str, sample: dict, write_header: bool) -> None:
    """Append one sample row to the CSV file.

    Args:
        output_file:  Path to the CSV file.
        sample:       Dict from collect_sample().
        write_header: If True, write the header row first.

    Key concept — append mode:
        open(path, 'a') opens the file for APPENDING. New data is added
        to the end without overwriting existing content. This is perfect
        for a logger that runs continuously.
    """
    # TODO: Open the file in append mode ('a') with newline='' (required for csv).
    # TODO: Create a csv.writer from the file object.
    # TODO: If write_header is True, write the header row first:
    #       writer.writerow(['timestamp', 'cpu_pct', 'mem_pct', 'disk_pct'])
    # TODO: Write the sample values as a row.
    pass


def run_logger(output_file: str, interval: float, max_samples: int) -> None:
    """Collect samples and write them to a CSV on a loop.

    Args:
        output_file:  Path to the output CSV file.
        interval:     Seconds between samples.
        max_samples:  Stop after this many samples (0 = run forever).
    """
    path = Path(output_file)

    # We only write the header if the file doesn't exist yet (or is empty).
    # This way, restarting the logger doesn't create duplicate headers.
    needs_header = not path.exists() or path.stat().st_size == 0

    print(f"\n  📊 Uptime Logger  →  {output_file}")
    print(f"  Interval: {interval}s  |  Max samples: {max_samples if max_samples else '∞'}")
    print("  Press Ctrl+C to stop.\n")
    print(f"  {'Timestamp':<22} {'CPU%':>6}  {'MEM%':>6}  {'DISK%':>6}")
    print("  " + "─" * 45)

    samples = 0
    try:
        while True:
            # TODO: Call collect_sample() to get a sample.
            # TODO: Call write_sample() to write it to the CSV.
            # TODO: Print the sample to the terminal as well (so the user sees it).
            # TODO: Increment samples counter.
            # TODO: If max_samples > 0 and samples >= max_samples, break.
            # TODO: Sleep for interval seconds.
            pass  # Remove and replace with your implementation

    except KeyboardInterrupt:
        print(f"\n\n  Stopped. {samples} sample(s) written to {output_file}\n")


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Log system stats to a CSV file.")
    parser.add_argument(
        "-o", "--output", default="stats.csv", help="Output CSV file (default: stats.csv)"
    )
    parser.add_argument(
        "-i", "--interval", type=float, default=5.0, help="Sample interval in seconds (default: 5)"
    )
    parser.add_argument(
        "-n",
        "--max-samples",
        type=int,
        default=0,
        help="Stop after N samples (default: run forever)",
    )
    args = parser.parse_args()

    run_logger(args.output, args.interval, args.max_samples)


# ── HINTS ─────────────────────────────────────────────────────────────────────
# 1. csv.writer writes lists as comma-separated rows.
#    writer.writerow(['a', 'b', 'c']) writes: a,b,c
# 2. Always open CSV files with newline='' to avoid double-spacing on Windows.
# 3. EXTENSION: Add network bytes_sent/bytes_recv to the CSV as well.
#    Use psutil.net_io_counters().bytes_sent etc.
# 4. EXTENSION: After collecting data, write a script to read it back with
#    csv.DictReader and print the average CPU usage.
