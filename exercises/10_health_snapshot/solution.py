"""
Exercise 10 — System Health Snapshot  ✅ SOLUTION
"""

import json
import socket
from datetime import datetime
from pathlib import Path

import psutil


def collect_cpu() -> dict:
    freq = psutil.cpu_freq()
    return {
        "percent":         psutil.cpu_percent(interval=1),
        "cores_physical":  psutil.cpu_count(logical=False),
        "cores_logical":   psutil.cpu_count(logical=True),
        "freq_mhz":        round(freq.current, 1) if freq else 0,
    }


def collect_memory() -> dict:
    m = psutil.virtual_memory()
    return {
        "total_gb":     round(m.total     / 1_073_741_824, 2),
        "used_gb":      round(m.used      / 1_073_741_824, 2),
        "available_gb": round(m.available / 1_073_741_824, 2),
        "percent":      m.percent,
    }


def collect_disk() -> dict:
    result = {}
    for part in psutil.disk_partitions():
        try:
            u = psutil.disk_usage(part.mountpoint)
            result[part.mountpoint] = {
                "total_gb": round(u.total / 1_073_741_824, 2),
                "used_gb":  round(u.used  / 1_073_741_824, 2),
                "free_gb":  round(u.free  / 1_073_741_824, 2),
                "percent":  u.percent,
            }
        except PermissionError:
            continue
    return result


def collect_top_processes(top_n: int = 5) -> list:
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
        try:
            rss = p.info["memory_info"].rss if p.info["memory_info"] else 0
            procs.append({
                "pid":     p.info["pid"],
                "name":    p.info["name"] or "",
                "cpu_pct": p.info["cpu_percent"] or 0.0,
                "mem_mb":  round(rss / 1_048_576, 1),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: x["cpu_pct"], reverse=True)
    return procs[:top_n]


def build_snapshot() -> dict:
    return {
        "generated_at":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hostname":       socket.gethostname(),
        "cpu":            collect_cpu(),
        "memory":         collect_memory(),
        "disk":           collect_disk(),
        "top_processes":  collect_top_processes(),
    }


def save_snapshot(snapshot: dict, output_dir: str) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = out / f"snapshot_{ts}.json"
    with open(path, "w") as f:
        json.dump(snapshot, f, indent=2)
    return path


def load_latest_snapshot(output_dir: str) -> dict | None:
    files = sorted(Path(output_dir).glob("snapshot_*.json"))
    if not files:
        return None
    with open(files[-1]) as f:
        return json.load(f)


def compare_snapshots(old: dict, new: dict) -> None:
    print("\n  📊 Snapshot Comparison\n")
    print(f"  Old: {old['generated_at']}   New: {new['generated_at']}\n")

    def delta(label: str, old_val: float, new_val: float, unit: str = "%") -> None:
        diff = new_val - old_val
        if diff > 0.5:
            arrow = f"\033[91m↑ +{diff:.1f}{unit}\033[0m"
        elif diff < -0.5:
            arrow = f"\033[92m↓ {diff:.1f}{unit}\033[0m"
        else:
            arrow = f"= {diff:+.1f}{unit}"
        print(f"  {label:<25} {old_val:.1f}{unit} → {new_val:.1f}{unit}  {arrow}")

    delta("CPU usage",    old["cpu"]["percent"],    new["cpu"]["percent"])
    delta("Memory usage", old["memory"]["percent"], new["memory"]["percent"])

    for mount, info in new["disk"].items():
        old_pct = old["disk"].get(mount, {}).get("percent", info["percent"])
        delta(f"Disk {mount}", old_pct, info["percent"])

    print()


def print_summary(snap: dict) -> None:
    print(f"\n  🖥️  Health Snapshot  —  {snap['generated_at']}")
    print(f"  Host: {snap['hostname']}")
    print(f"  CPU:  {snap['cpu']['percent']}%")
    print(f"  RAM:  {snap['memory']['percent']}%  ({snap['memory']['used_gb']} / {snap['memory']['total_gb']} GB)")
    for mount, d in snap["disk"].items():
        print(f"  Disk {mount}: {d['percent']}%")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="snapshots")
    parser.add_argument("--compare", action="store_true")
    args = parser.parse_args()

    if args.compare:
        previous = load_latest_snapshot(args.output)

    snapshot = build_snapshot()

    if args.compare and previous:
        compare_snapshots(previous, snapshot)

    saved = save_snapshot(snapshot, args.output)
    print_summary(snapshot)
    print(f"\n  Saved: {saved}\n")
