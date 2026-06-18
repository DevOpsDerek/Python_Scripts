"""
ping_hosts.py — Ping multiple hosts concurrently and report results
====================================================================
Concepts covered:
  - subprocess.run()   (running shell commands from Python)
  - concurrent.futures.ThreadPoolExecutor (parallel execution)
  - platform.system()  (cross-platform command differences)
  - Parsing command output (stdout/stderr)
  - Rich formatted tables
"""

import platform
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional


@dataclass
class PingResult:
    host: str
    reachable: bool
    avg_ms: Optional[float] = None
    packet_loss: float = 0.0
    error: str = ""


def ping_host(host: str, count: int = 3) -> PingResult:
    """Ping a single host and return the result.

    Args:
        host:  Hostname or IP address.
        count: Number of ICMP packets to send.

    Returns:
        A PingResult dataclass with reachability and latency info.
    """
    # The ping command syntax differs between operating systems
    os_name = platform.system()
    if os_name == "Windows":
        # Windows: ping -n <count> <host>
        cmd = ["ping", "-n", str(count), host]
    else:
        # macOS/Linux: ping -c <count> -W 2 <host>  (-W sets timeout per packet)
        cmd = ["ping", "-c", str(count), "-W", "2", host]

    try:
        # subprocess.run() runs the command and captures its output
        result = subprocess.run(
            cmd,
            capture_output=True,  # capture both stdout and stderr
            text=True,  # decode bytes to string automatically
            timeout=count * 3,  # overall timeout: count × 3 seconds
        )

        output = result.stdout + result.stderr
        reachable = result.returncode == 0

        # --- Parse average RTT ---
        avg_ms = None
        # Linux/macOS output includes a line like: rtt min/avg/max/mdev = 1.2/2.3/3.4/0.5 ms
        # Windows output: Average = 2ms
        if os_name != "Windows":
            for line in output.splitlines():
                if "rtt" in line or "round-trip" in line:
                    parts = line.split("=")[-1].strip().split("/")
                    try:
                        avg_ms = float(parts[1])  # avg is the second value
                    except (IndexError, ValueError):
                        pass
        else:
            for line in output.splitlines():
                if "Average" in line:
                    try:
                        avg_ms = float(line.split("=")[-1].strip().replace("ms", ""))
                    except ValueError:
                        pass

        # --- Parse packet loss ---
        packet_loss = 0.0
        for line in output.splitlines():
            if "packet loss" in line.lower() or "loss" in line.lower():
                for token in line.split():
                    if "%" in token:
                        try:
                            packet_loss = float(token.strip("%,"))
                        except ValueError:
                            pass
                break

        return PingResult(host=host, reachable=reachable, avg_ms=avg_ms, packet_loss=packet_loss)

    except subprocess.TimeoutExpired:
        return PingResult(host=host, reachable=False, error="timeout")
    except FileNotFoundError:
        return PingResult(host=host, reachable=False, error="ping not found")


def ping_all(hosts: list, count: int = 3, workers: int = 10) -> list:
    """Ping all hosts in parallel using a thread pool.

    Args:
        hosts:   List of hostnames/IPs to ping.
        count:   ICMP packets per host.
        workers: Maximum parallel ping threads.

    Returns:
        List of PingResult objects in original host order.
    """
    results = {}

    # ThreadPoolExecutor manages a pool of threads so we don't spin up N threads
    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all ping jobs and get a dict of {future: host}
        futures = {executor.submit(ping_host, host, count): host for host in hosts}

        for future in as_completed(futures):  # Process results as they come in
            result = future.result()
            results[result.host] = result

    # Return in original order for consistent output
    return [results[h] for h in hosts if h in results]


def print_results(results: list) -> None:
    """Display ping results in a colour-coded table."""
    reachable = [r for r in results if r.reachable]

    print(f"\n  PING RESULTS  ({len(reachable)}/{len(results)} reachable)\n")
    print(f"  {'Host':<30} {'Status':<12} {'Avg RTT':>10}  {'Loss':>6}")
    print("  " + "─" * 65)

    for r in results:
        if r.reachable:
            status = "\033[92m✓ ALIVE\033[0m"
            rtt = f"{r.avg_ms:.1f} ms" if r.avg_ms else "  N/A"
            loss = f"{r.packet_loss:.0f}%"
        else:
            status = "\033[91m✗ DOWN \033[0m"
            rtt = "  N/A"
            loss = "100%"
            if r.error:
                loss = r.error

        print(f"  {r.host:<30} {status:<20} {rtt:>10}  {loss:>6}")

    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ping multiple hosts in parallel.")
    parser.add_argument("hosts", nargs="*", help="Hostnames or IPs to ping")
    parser.add_argument("-f", "--file", help="File with one host per line")
    parser.add_argument("-c", "--count", type=int, default=3, help="Packets per host (default: 3)")
    parser.add_argument(
        "-w", "--workers", type=int, default=10, help="Parallel threads (default: 10)"
    )
    args = parser.parse_args()

    host_list = args.hosts or []

    if args.file:
        with open(args.file) as f:
            host_list += [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not host_list:
        # Default demo targets if none supplied
        host_list = ["8.8.8.8", "1.1.1.1", "google.com", "github.com", "192.168.1.1", "10.0.0.1"]
        print(f"  No hosts specified — using demo list: {host_list}")

    print(f"\n  Pinging {len(host_list)} host(s) with {args.count} packets each…")
    results = ping_all(host_list, count=args.count, workers=args.workers)
    print_results(results)

# ---------------------------------------------------------------------------
# TRY THIS:
#   python ping_hosts.py 8.8.8.8 1.1.1.1 google.com
#   python ping_hosts.py -f hosts.txt
#   echo -e "8.8.8.8\ngoogle.com" > hosts.txt && python ping_hosts.py -f hosts.txt
# ---------------------------------------------------------------------------
