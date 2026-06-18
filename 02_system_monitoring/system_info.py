"""
system_info.py — Display a comprehensive system information snapshot
====================================================================
Concepts covered:
  - psutil         (cross-platform system & process utilities)
  - platform       (OS and hardware information)
  - socket         (hostname and network name)
  - dataclasses    (clean data containers)
  - datetime       (uptime calculations)
  - String formatting and terminal output
"""

import platform
import socket
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict

import psutil  # pip install psutil


@dataclass
class SystemSnapshot:
    """A dataclass holding all the system info we want to display.

    Dataclasses automatically generate __init__, __repr__, and __eq__
    so we don't have to write boilerplate code.
    """

    hostname: str = ""
    os_name: str = ""
    os_version: str = ""
    architecture: str = ""
    python_version: str = ""
    cpu_model: str = ""
    cpu_cores_physical: int = 0
    cpu_cores_logical: int = 0
    cpu_freq_mhz: float = 0.0
    ram_total_gb: float = 0.0
    ram_available_gb: float = 0.0
    ram_percent: float = 0.0
    disk_info: Dict[str, dict] = field(default_factory=dict)
    boot_time: datetime = field(default_factory=datetime.now)
    uptime: timedelta = field(default_factory=lambda: timedelta(0))


def collect_system_info() -> SystemSnapshot:
    """Gather system information and return it as a SystemSnapshot."""
    snap = SystemSnapshot()

    # --- Identity ---
    snap.hostname = socket.gethostname()
    snap.os_name = platform.system()  # e.g. 'Darwin', 'Linux', 'Windows'
    snap.os_version = platform.version()
    snap.architecture = platform.machine()  # e.g. 'x86_64', 'arm64'
    snap.python_version = platform.python_version()

    # --- CPU ---
    # psutil.cpu_freq() returns current/min/max MHz; not available on all
    # platforms (e.g. macOS ARM64 raises AttributeError), so guard with getattr.
    _cpu_freq_fn = getattr(psutil, "cpu_freq", None)
    freq = _cpu_freq_fn() if _cpu_freq_fn is not None else None
    snap.cpu_freq_mhz = freq.current if freq else 0.0
    snap.cpu_cores_physical = psutil.cpu_count(logical=False) or 0
    snap.cpu_cores_logical = psutil.cpu_count(logical=True) or 0

    # platform.processor() gives a human-readable CPU description on most OSes
    snap.cpu_model = platform.processor() or "Unknown"

    # --- Memory ---
    mem = psutil.virtual_memory()  # Returns a named tuple with total, available, percent, etc.
    snap.ram_total_gb = mem.total / 1_073_741_824  # bytes → GB (1 GB = 1024³ bytes)
    snap.ram_available_gb = mem.available / 1_073_741_824
    snap.ram_percent = mem.percent

    # --- Disks ---
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            snap.disk_info[partition.mountpoint] = {
                "device": partition.device,
                "fstype": partition.fstype,
                "total_gb": usage.total / 1_073_741_824,
                "used_gb": usage.used / 1_073_741_824,
                "free_gb": usage.free / 1_073_741_824,
                "percent": usage.percent,
            }
        except PermissionError:
            # Some mount points (like /proc on Linux) aren't accessible
            pass

    # --- Uptime ---
    boot_ts = psutil.boot_time()  # Unix timestamp of last boot
    snap.boot_time = datetime.fromtimestamp(boot_ts)
    snap.uptime = datetime.now() - snap.boot_time

    return snap


def render_bar(percent: float, width: int = 30) -> str:
    """Draw a simple ASCII progress bar.

    Example: render_bar(65) → '[█████████████████░░░░░░░░░░░░░] 65.0%'
    """
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percent:.1f}%"


def print_system_info(snap: SystemSnapshot) -> None:
    """Display the system snapshot in a formatted, readable layout."""
    w = 60  # Total line width

    print("\n" + "=" * w)
    print("  🖥️  SYSTEM INFORMATION SNAPSHOT")
    print("=" * w)

    # --- System Identity ---
    print("\n  System")
    print(f"  {'Hostname':<20} {snap.hostname}")
    print(f"  {'OS':<20} {snap.os_name}")
    print(f"  {'Architecture':<20} {snap.architecture}")
    print(f"  {'Python':<20} {snap.python_version}")

    days = snap.uptime.days
    hours, remainder = divmod(snap.uptime.seconds, 3600)
    minutes = remainder // 60
    print(f"  {'Boot Time':<20} {snap.boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  {'Uptime':<20} {days}d {hours}h {minutes}m")

    # --- CPU ---
    print("\n  CPU")
    print(f"  {'Model':<20} {snap.cpu_model[:38]}")
    print(f"  {'Cores (physical)':<20} {snap.cpu_cores_physical}")
    print(f"  {'Cores (logical)':<20} {snap.cpu_cores_logical}")
    if snap.cpu_freq_mhz:
        print(f"  {'Frequency':<20} {snap.cpu_freq_mhz:.0f} MHz")

    # Show a 1-second CPU usage sample
    cpu_pct = psutil.cpu_percent(interval=1)
    print(f"  {'Usage (1s)':<20} {render_bar(cpu_pct)}")

    # --- Memory ---
    print("\n  Memory")
    print(f"  {'Total':<20} {snap.ram_total_gb:.1f} GB")
    print(f"  {'Available':<20} {snap.ram_available_gb:.1f} GB")
    print(f"  {'Usage':<20} {render_bar(snap.ram_percent)}")

    # --- Disks ---
    print("\n  Disk Partitions")
    for mount, info in snap.disk_info.items():
        print(f"\n  Mount: {mount}  [{info['fstype']}]  ({info['device']})")
        print(f"  {'Total':<20} {info['total_gb']:.1f} GB")
        print(f"  {'Used':<20} {info['used_gb']:.1f} GB  (free: {info['free_gb']:.1f} GB)")
        print(f"  {'Usage':<20} {render_bar(info['percent'])}")

    print("\n" + "=" * w + "\n")


if __name__ == "__main__":
    snapshot = collect_system_info()
    print_system_info(snapshot)

# ---------------------------------------------------------------------------
# TRY THIS:
#   python system_info.py
#   # Then try modifying render_bar() to use different characters
# ---------------------------------------------------------------------------
