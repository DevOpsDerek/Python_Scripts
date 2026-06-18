"""
Exercise 10 — System Health Snapshot (ADVANCED)
=================================================
GOAL: Combine everything you've learned to write a script that:
  1. Collects CPU, memory, disk, and top-process data using psutil
  2. Structures the data as a Python dict
  3. Saves it as a timestamped JSON file
  4. Optionally compares to a previous snapshot and reports changes

Expected JSON output (snapshot_2024-06-18_10-30-00.json):
    {
        "generated_at": "2024-06-18 10:30:00",
        "hostname": "myhost",
        "cpu": { "percent": 14.2, "cores": 8, "freq_mhz": 2400 },
        "memory": { "total_gb": 16.0, "used_gb": 7.3, "percent": 45.6 },
        "disk": { "/": { "total_gb": 500.0, "used_gb": 231.0, "percent": 46.2 } },
        "top_processes": [
            { "pid": 1234, "name": "python", "cpu_pct": 12.1, "mem_mb": 145.2 },
            ...
        ]
    }

CONCEPTS YOU WILL PRACTISE:
  - json module            — json.dumps(), json.dump(), json.load()
  - Nested dicts           — building structured data
  - psutil                 — combining multiple metric sources
  - datetime               — timestamp generation
  - File I/O               — writing and reading JSON files
  - Comparing dicts        — detecting changes between snapshots

HOW TO RUN:
    python exercise.py                    (save snapshot, print summary)
    python exercise.py --compare          (compare to most recent snapshot)
    python exercise.py --output /tmp/snap (custom output directory)
"""

from pathlib import Path

# ── Step 1: Collect Data ─────────────────────────────────────────────────────


def collect_cpu() -> dict:
    """Return a dict with CPU metrics.

    Keys to include: percent, cores_physical, cores_logical, freq_mhz.
    Set freq_mhz to 0 if psutil.cpu_freq() returns None.
    """
    # TODO: Use psutil.cpu_percent(interval=1), psutil.cpu_count(),
    # and psutil.cpu_freq() to build and return the dict.
    pass


def collect_memory() -> dict:
    """Return a dict with memory metrics.

    Keys: total_gb, used_gb, available_gb, percent.
    Convert bytes to GB by dividing by 1_073_741_824.
    """
    # TODO: Use psutil.virtual_memory() to get memory stats.
    pass


def collect_disk() -> dict:
    """Return a dict mapping mount point → usage stats.

    Structure: { "/": { "total_gb": ..., "used_gb": ..., "free_gb": ..., "percent": ... } }
    Skip partitions that raise PermissionError.

    Hint: Use psutil.disk_partitions() and psutil.disk_usage(mount).
    """
    # TODO: Build and return the nested dict.
    pass


def collect_top_processes(top_n: int = 5) -> list:
    """Return a list of the top N processes by CPU usage.

    Each entry should be a dict with keys: pid, name, cpu_pct, mem_mb.
    Sort by cpu_pct descending.

    Hint: Use psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']).
    memory_info.rss gives RAM in bytes — convert to MB.
    """
    # TODO: Collect process info and return the top N sorted by CPU.
    pass


def build_snapshot() -> dict:
    """Combine all metric collectors into a single snapshot dict.

    The top-level structure should be:
    {
        "generated_at": "<timestamp>",
        "hostname": "<hostname>",
        "cpu": { ... },
        "memory": { ... },
        "disk": { ... },
        "top_processes": [ ... ]
    }
    """
    # TODO: Call each collector function and assemble the snapshot dict.
    # TODO: Include "generated_at" (formatted datetime) and "hostname".
    pass


# ── Step 2: Save & Load ───────────────────────────────────────────────────────


def save_snapshot(snapshot: dict, output_dir: str) -> Path:
    """Save the snapshot dict as a JSON file.

    Filename format: snapshot_<YYYY-MM-DD_HH-MM-SS>.json

    Args:
        snapshot:   The snapshot dict.
        output_dir: Directory to save the file.

    Returns:
        Path to the saved file.

    Hint: json.dump(data, file, indent=2) writes pretty-printed JSON.
    """
    # TODO: Create the output directory if it doesn't exist.
    # TODO: Build a timestamped filename.
    # TODO: Write snapshot to the file using json.dump().
    # TODO: Return the Path to the saved file.
    pass


def load_latest_snapshot(output_dir: str) -> dict | None:
    """Load the most recent snapshot JSON file from output_dir.

    Returns None if no snapshot files exist.

    Hint: Use glob to find all snapshot_*.json files,
    then sort by name (timestamps sort alphabetically!).
    """
    # TODO: Find all snapshot_*.json files in output_dir.
    # TODO: Sort them and return the contents of the last one.
    # Hint: json.load(file) reads a JSON file into a Python dict.
    pass


# ── Step 3: Compare ───────────────────────────────────────────────────────────


def compare_snapshots(old: dict, new: dict) -> None:
    """Print a comparison between two snapshots, highlighting changes.

    Compare: cpu.percent, memory.percent, and disk usage per mount.
    Show the delta (new - old) for each metric.
    """
    print("\n  📊 Snapshot Comparison\n")

    def delta(label: str, old_val: float, new_val: float, unit: str = "%") -> None:
        """Print a metric with its change."""
        # TODO: Calculate diff = new_val - old_val.
        # TODO: Print with an up/down arrow or = based on whether it increased/decreased.
        # Hint: use ↑ for increase (red), ↓ for decrease (green), = for no change.
        pass

    # TODO: Compare cpu.percent, memory.percent.
    # TODO: Compare disk percent for each mount point in new['disk'].
    pass


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Save a system health snapshot to JSON.")
    parser.add_argument(
        "--output", default="snapshots", help="Output directory (default: snapshots)"
    )
    parser.add_argument(
        "--compare", action="store_true", help="Compare to the most recent snapshot"
    )
    args = parser.parse_args()

    # TODO: Build the snapshot.
    # TODO: If --compare is set, load the previous snapshot and call compare_snapshots().
    # TODO: Save the new snapshot and print confirmation.
    # TODO: Print a summary of key metrics to the terminal.


# ── HINTS ─────────────────────────────────────────────────────────────────────
# 1. json.dumps(data, indent=2) converts a dict to a formatted JSON string.
# 2. json.dump(data, file_object, indent=2) writes it directly to a file.
# 3. json.load(file_object) reads a JSON file back into a Python dict.
# 4. Timestamps sort lexicographically if formatted as YYYY-MM-DD_HH-MM-SS,
#    so sorted(files)[-1] gives the most recent file.
# 5. EXTENSION: Schedule this script with cron to run every hour, then write
#    a second script that reads all snapshots and plots a graph using matplotlib.
