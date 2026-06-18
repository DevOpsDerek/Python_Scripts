"""
send_report.py — Generate and email a system health report
===========================================================
Concepts covered:
  - smtplib        (sending emails via SMTP)
  - email.mime     (building multi-part email messages)
  - psutil         (gathering system stats)
  - string.Template (simple text templating)
  - os.environ     (reading config from environment variables)
  - argparse
"""

import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template

import psutil  # pip install psutil

# ---------------------------------------------------------------------------
# Report template — Python's string.Template uses $variable syntax.
# It's simpler than format strings for long multi-line templates.
# ---------------------------------------------------------------------------
REPORT_TEMPLATE = Template("""
System Health Report
====================
Generated: $timestamp
Hostname:  $hostname

CPU
---
Usage (1s avg):  $cpu_pct%
Physical cores:  $cpu_cores
Load average:    $load_avg

Memory
------
Total:     $mem_total GB
Used:      $mem_used GB
Available: $mem_free GB
Usage:     $mem_pct%

Disk (/)
--------
Total:  $disk_total GB
Used:   $disk_used GB
Free:   $disk_free GB
Usage:  $disk_pct%

Top 5 CPU Processes
-------------------
$top_procs

--
Sent by send_report.py
""")


def gather_stats() -> dict:
    """Collect system statistics and return them as a template-ready dict."""
    import socket

    # CPU — first call primes the counter; we use a 1-second interval
    cpu_pct = psutil.cpu_percent(interval=1)
    cores = psutil.cpu_count(logical=False) or 0
    load = psutil.getloadavg() if hasattr(psutil, "getloadavg") else (0, 0, 0)

    # Memory
    mem = psutil.virtual_memory()

    # Disk
    try:
        disk = psutil.disk_usage("/")
        disk_total = f"{disk.total / 1e9:.1f}"
        disk_used = f"{disk.used / 1e9:.1f}"
        disk_free = f"{disk.free / 1e9:.1f}"
        disk_pct = disk.percent
    except Exception:
        disk_total = disk_used = disk_free = "N/A"
        disk_pct = 0

    # Top 5 processes by CPU
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    procs.sort(key=lambda x: x["cpu_percent"] or 0, reverse=True)
    top_procs_lines = [
        f"  {p['pid']:<8} {(p['name'] or '')[:20]:<22} CPU: {p['cpu_percent'] or 0:.1f}%  MEM: {p['memory_percent'] or 0:.1f}%"
        for p in procs[:5]
    ]

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hostname": socket.gethostname(),
        "cpu_pct": f"{cpu_pct:.1f}",
        "cpu_cores": cores,
        "load_avg": f"{load[0]:.2f}  {load[1]:.2f}  {load[2]:.2f}  (1m/5m/15m)",
        "mem_total": f"{mem.total / 1e9:.1f}",
        "mem_used": f"{mem.used / 1e9:.1f}",
        "mem_free": f"{mem.available / 1e9:.1f}",
        "mem_pct": mem.percent,
        "disk_total": disk_total,
        "disk_used": disk_used,
        "disk_free": disk_free,
        "disk_pct": disk_pct,
        "top_procs": "\n".join(top_procs_lines) if top_procs_lines else "  (none)",
    }


def build_report() -> str:
    """Generate the report text."""
    stats = gather_stats()
    return REPORT_TEMPLATE.substitute(stats)


def send_email(
    report: str,
    to_addr: str,
    from_addr: str,
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_pass: str,
    use_tls: bool = True,
) -> None:
    """Send the report as an email.

    Args:
        report:    The report text body.
        to_addr:   Recipient email address.
        from_addr: Sender email address.
        smtp_host: SMTP server hostname.
        smtp_port: SMTP server port.
        smtp_user: SMTP login username.
        smtp_pass: SMTP login password.
        use_tls:   Use STARTTLS (default True).
    """
    # MIMEMultipart lets us attach both plain text and HTML parts
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"System Health Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    msg["From"] = from_addr
    msg["To"] = to_addr

    # Attach the plain-text version
    msg.attach(MIMEText(report, "plain"))

    # Simple HTML version (wrap pre-formatted text)
    html_body = f"<html><body><pre style='font-family:monospace'>{report}</pre></body></html>"
    msg.attach(MIMEText(html_body, "html"))

    print(f"  Connecting to {smtp_host}:{smtp_port}…")

    # smtplib.SMTP manages the connection lifecycle
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        if use_tls:
            server.starttls()  # Upgrade connection to TLS
        server.login(smtp_user, smtp_pass)
        server.sendmail(from_addr, to_addr, msg.as_string())

    print(f"  ✅ Report sent to {to_addr}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate and email a system health report.")
    parser.add_argument("--to", help="Recipient email address")
    parser.add_argument("--from-addr", help="Sender email address")
    parser.add_argument(
        "--smtp-host", default="smtp.gmail.com", help="SMTP server (default: smtp.gmail.com)"
    )
    parser.add_argument("--smtp-port", type=int, default=587, help="SMTP port (default: 587)")
    parser.add_argument(
        "--print-only", action="store_true", help="Print the report without sending"
    )
    args = parser.parse_args()

    report = build_report()

    if args.print_only or not args.to:
        print(report)
    else:
        # Read credentials from environment variables — NEVER hard-code passwords!
        smtp_user = os.environ.get("SMTP_USER", args.from_addr)
        smtp_pass = os.environ.get("SMTP_PASS", "")

        if not smtp_pass:
            print("  ❌ Set SMTP_PASS environment variable before sending email.")
            print("     export SMTP_PASS='your-app-password'")
            raise SystemExit(1)

        send_email(
            report=report,
            to_addr=args.to,
            from_addr=args.from_addr or smtp_user,
            smtp_host=args.smtp_host,
            smtp_port=args.smtp_port,
            smtp_user=smtp_user,
            smtp_pass=smtp_pass,
        )

# ---------------------------------------------------------------------------
# TRY THIS:
#   python send_report.py --print-only          # preview report in terminal
#   export SMTP_PASS="your-gmail-app-password"
#   python send_report.py --to you@example.com --from-addr from@gmail.com
# ---------------------------------------------------------------------------
