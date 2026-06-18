"""
port_scanner.py — Scan a host for open TCP ports
=================================================
Concepts covered:
  - socket module   (low-level network connections)
  - threading       (concurrent.futures.ThreadPoolExecutor)
  - Timeouts        (socket.settimeout)
  - Well-known ports (service names)
  - Generator expressions in sorted()
"""

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

# Common port → service name mapping for friendly output
WELL_KNOWN_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    465: "SMTPS",
    587: "SMTP (submission)",
    993: "IMAPS",
    995: "POP3S",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    8080: "HTTP-alt",
    8443: "HTTPS-alt",
    27017: "MongoDB",
}


def check_port(host: str, port: int, timeout: float = 0.5) -> Optional[int]:
    """Try to open a TCP connection to host:port.

    A successful connection means the port is open (something is listening).
    A refused/timed-out connection means the port is closed or filtered.

    Args:
        host:    Target hostname or IP.
        port:    Port number (1–65535).
        timeout: Seconds to wait before giving up.

    Returns:
        The port number if open, None if closed/filtered.
    """
    # socket.AF_INET = IPv4, socket.SOCK_STREAM = TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)  # Don't wait forever for a response
        try:
            # connect_ex() returns 0 on success (port open), non-zero on failure
            result = sock.connect_ex((host, port))
            return port if result == 0 else None
        except (OSError, socket.timeout):
            return None


def resolve_host(host: str) -> Optional[str]:
    """Resolve a hostname to an IP address.

    Args:
        host: Hostname or IP string.

    Returns:
        IP address string, or None if resolution fails.
    """
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return None


def scan_ports(
    host: str,
    start_port: int = 1,
    end_port: int = 1024,
    workers: int = 100,
    timeout: float = 0.5,
) -> list:
    """Scan a range of TCP ports on a host using parallel threads.

    Args:
        host:       Target hostname or IP.
        start_port: First port to scan.
        end_port:   Last port to scan (inclusive).
        workers:    Number of concurrent threads.
        timeout:    Per-port connection timeout in seconds.

    Returns:
        Sorted list of open port numbers.
    """
    ip = resolve_host(host)
    if not ip:
        print(f"  ❌ Cannot resolve hostname: {host}")
        return []

    print(f"\n  🔍 Scanning {host} ({ip})")
    print(f"     Ports {start_port}–{end_port}  |  {workers} threads  |  {timeout}s timeout\n")

    open_ports = []
    total = end_port - start_port + 1
    scanned = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all port checks at once
        futures = {
            executor.submit(check_port, ip, port, timeout): port
            for port in range(start_port, end_port + 1)
        }

        for future in as_completed(futures):
            scanned += 1
            result = future.result()
            if result is not None:
                open_ports.append(result)

            # Progress indicator (overwrite same line)
            pct = scanned / total * 100
            print(f"  Progress: {scanned}/{total}  ({pct:.0f}%)  Open: {len(open_ports)}", end="\r")

    print()  # Newline after progress line
    return sorted(open_ports)


def print_results(host: str, open_ports: list) -> None:
    """Display scan results in a clean table."""
    print(f"\n  {'─' * 50}")

    if not open_ports:
        print(f"  No open ports found on {host}.")
    else:
        print(f"  Open ports on {host}:\n")
        print(f"  {'Port':<8} {'Service':<25} {'State'}")
        print(f"  {'─' * 45}")
        for port in open_ports:
            service = WELL_KNOWN_PORTS.get(port, "unknown")
            print(f"  {port:<8} {service:<25} \033[92mopen\033[0m")

    print(f"\n  Total open: {len(open_ports)}")
    print(f"  {'─' * 50}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scan open TCP ports on a host.")
    parser.add_argument("host", help="Target hostname or IP address")
    parser.add_argument("-s", "--start", type=int, default=1, help="Start port (default: 1)")
    parser.add_argument("-e", "--end", type=int, default=1024, help="End port (default: 1024)")
    parser.add_argument(
        "-w", "--workers", type=int, default=100, help="Concurrent threads (default: 100)"
    )
    parser.add_argument(
        "-t", "--timeout", type=float, default=0.5, help="Per-port timeout seconds (default: 0.5)"
    )
    args = parser.parse_args()

    open_ports = scan_ports(args.host, args.start, args.end, args.workers, args.timeout)
    print_results(args.host, open_ports)

# ---------------------------------------------------------------------------
# TRY THIS (scan your own machine — always safe and educational):
#   python port_scanner.py localhost
#   python port_scanner.py localhost -s 1 -e 65535
#   python port_scanner.py 127.0.0.1 -s 8000 -e 9000
#
# ⚠️  WARNING: Only scan hosts you own or have explicit permission to scan.
#     Unauthorised port scanning may be illegal.
# ---------------------------------------------------------------------------
