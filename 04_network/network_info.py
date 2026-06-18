"""
network_info.py — Display network interface and routing information
===================================================================
Concepts covered:
  - psutil.net_if_addrs()     (interface addresses)
  - psutil.net_if_stats()     (interface speed, MTU, status)
  - psutil.net_io_counters()  (bytes sent/received)
  - socket                    (hostname, DNS resolution)
  - subprocess                (calling system tools like ip/netstat)
  - String formatting
"""

import socket

import psutil  # pip install psutil


def bytes_to_human(b: int) -> str:
    """Human-readable byte count (KB/MB/GB/TB)."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


def get_public_ip() -> str:
    """Try to determine the machine's public IP by connecting to a known host.

    We don't actually send any data — just opening a UDP socket lets the OS
    choose which local IP it would use for routing to 8.8.8.8.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # UDP connect — no data sent
            return s.getsockname()[0]    # Returns the local IP used for routing
    except Exception:
        return "N/A"


def show_hostname() -> None:
    """Display hostname and basic DNS information."""
    hostname = socket.gethostname()
    try:
        host_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        host_ip = "N/A"

    print(f"\n  {'─' * 55}")
    print("  🌐  NETWORK INFORMATION")
    print(f"  {'─' * 55}")
    print(f"  {'Hostname':<25} {hostname}")
    print(f"  {'Host IP':<25} {host_ip}")
    print(f"  {'Routing IP':<25} {get_public_ip()}")
    print(f"  {'FQDN':<25} {socket.getfqdn()}")


def show_interfaces() -> None:
    """Show all network interfaces with their addresses and statistics."""
    addrs = psutil.net_if_addrs()       # {iface: [snic(...)]}
    stats = psutil.net_if_stats()       # {iface: snicstats(...)}
    io    = psutil.net_io_counters(pernic=True)  # {iface: snetio(...)}

    # Address family constants
    AF_INET  = socket.AF_INET   # IPv4
    AF_INET6 = socket.AF_INET6  # IPv6
    AF_LINK  = psutil.AF_LINK   # MAC address

    print(f"\n  {'─' * 55}")
    print("  🔌  NETWORK INTERFACES")

    for iface_name in sorted(addrs.keys()):
        iface_stats = stats.get(iface_name)
        iface_io    = io.get(iface_name)

        # Status badge
        if iface_stats and iface_stats.isup:
            status = "\033[92m▲ UP\033[0m"
        else:
            status = "\033[91m▼ DOWN\033[0m"

        print(f"\n  {'─' * 55}")
        print(f"  Interface: \033[1m{iface_name}\033[0m  {status}")

        # Statistics (speed, MTU)
        if iface_stats:
            speed = f"{iface_stats.speed} Mbps" if iface_stats.speed else "unknown"
            print(f"  {'Speed':<20} {speed}")
            print(f"  {'MTU':<20} {iface_stats.mtu} bytes")
            print(f"  {'Duplex':<20} {iface_stats.duplex.name if iface_stats.duplex else 'N/A'}")

        # Addresses (IPv4, IPv6, MAC)
        for snic in addrs[iface_name]:
            if snic.family == AF_INET:
                print(f"  {'IPv4':<20} {snic.address}  (netmask: {snic.netmask})")
            elif snic.family == AF_INET6:
                # IPv6 addresses can be very long — trim if needed
                addr = snic.address.split("%")[0]  # Remove interface suffix like %eth0
                print(f"  {'IPv6':<20} {addr}")
            elif snic.family == AF_LINK:
                print(f"  {'MAC':<20} {snic.address}")

        # I/O counters
        if iface_io:
            print(f"  {'Bytes sent':<20} {bytes_to_human(iface_io.bytes_sent)}")
            print(f"  {'Bytes received':<20} {bytes_to_human(iface_io.bytes_recv)}")
            print(f"  {'Packets sent':<20} {iface_io.packets_sent:,}")
            print(f"  {'Packets recv':<20} {iface_io.packets_recv:,}")
            if iface_io.errin or iface_io.errout:
                print(f"  {'Errors in/out':<20} {iface_io.errin} / {iface_io.errout}")

    print(f"  {'─' * 55}\n")


def show_connections(kind: str = "inet") -> None:
    """Show active network connections.

    Args:
        kind: Connection type — 'inet' (TCP+UDP), 'tcp', 'udp', or 'all'.
    """
    try:
        conns = psutil.net_connections(kind=kind)
    except psutil.AccessDenied:
        print("  ⚠️  Access denied — run with sudo to see all connections.")
        return

    # Filter to established or listening connections for a cleaner view
    active = [c for c in conns if c.status in ("ESTABLISHED", "LISTEN")]

    print(f"  {'─' * 55}")
    print(f"  🔗  ACTIVE CONNECTIONS  ({len(active)} of {len(conns)} shown)\n")
    print(f"  {'Proto':<7} {'Local Address':<25} {'Remote Address':<25} {'Status':<14} {'PID'}")
    print("  " + "─" * 90)

    for c in sorted(active, key=lambda x: x.status):
        proto = "TCP" if c.type == socket.SOCK_STREAM else "UDP"
        laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "-"
        raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "-"
        status = c.status or "-"
        pid = str(c.pid) if c.pid else "-"
        print(f"  {proto:<7} {laddr:<25} {raddr:<25} {status:<14} {pid}")

    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Show network interfaces and connections.")
    parser.add_argument("--connections", action="store_true", help="Show active TCP/UDP connections")
    args = parser.parse_args()

    show_hostname()
    show_interfaces()
    if args.connections:
        show_connections()

# ---------------------------------------------------------------------------
# TRY THIS:
#   python network_info.py
#   python network_info.py --connections
# ---------------------------------------------------------------------------
