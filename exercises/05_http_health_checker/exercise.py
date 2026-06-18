"""
Exercise 05 — HTTP Health Checker
===================================
GOAL: Write a script that checks whether a list of URLs is reachable
and responding with HTTP 200 OK.

Expected output example:
    HTTP Health Check  (timeout: 5s)
    ─────────────────────────────────────────────────────────
    ✅  200  https://google.com           (0.23s)
    ✅  200  https://github.com           (0.41s)
    ❌  503  https://httpstat.us/503      (0.18s)  ← non-200
    ❌  ERR  https://doesnotexist.xyz     timeout

    3/4 healthy

CONCEPTS YOU WILL PRACTISE:
  - urllib.request         — making HTTP requests (no extra packages needed!)
  - time.time()            — measuring elapsed time
  - Exception handling     — URLError, timeout, connection refused
  - concurrent.futures     — parallel checks (BONUS)

HOW TO RUN:
    python exercise.py
    python exercise.py --urls https://google.com https://github.com
    python exercise.py --file urls.txt
"""

import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class CheckResult:
    url: str
    status: Optional[int]  # HTTP status code, or None on error
    elapsed_s: float  # How long the request took in seconds
    error: str = ""  # Error message if request failed


def check_url(url: str, timeout: float = 5.0) -> CheckResult:
    """Make an HTTP GET request to *url* and return the result.

    Args:
        url:     The URL to check (must include http:// or https://).
        timeout: Seconds to wait for a response before giving up.

    Returns:
        A CheckResult dataclass.

    Hints:
      - Use urllib.request.urlopen(url, timeout=timeout).
      - The response object has a .status (or .getcode()) attribute.
      - urllib.error.URLError is raised for network errors.
      - urllib.error.HTTPError (a subclass of URLError) is raised for
        non-2xx responses. It has a .code attribute for the status code.
      - Wrap in try/except to handle both cases.
      - Use time.time() before and after the request to measure elapsed time.
    """
    start = time.time()

    # TODO: Try to open the URL with urllib.request.urlopen().
    # TODO: On success, capture the status code and return a CheckResult.
    # TODO: On urllib.error.HTTPError, capture the error code (it's still useful).
    # TODO: On urllib.error.URLError or any other Exception, set error message.
    # TODO: Always calculate elapsed = time.time() - start.

    pass  # Replace with your implementation


def print_report(results: list, timeout: float) -> None:
    """Print a health check report."""
    print(f"\n  HTTP Health Check  (timeout: {timeout}s)")
    print("  " + "─" * 60)

    healthy = 0
    for r in results:
        elapsed = f"({r.elapsed_s:.2f}s)"

        # TODO: Determine the icon and colour:
        #   status 200       → ✅ green
        #   other status     → ⚠️  yellow
        #   error (no status) → ❌ red
        # TODO: Format and print the row. Something like:
        #   f"  {icon}  {status_str:<5}  {r.url:<45} {elapsed}"

        pass  # Replace with your print logic

    print(f"\n  {healthy}/{len(results)} healthy\n")


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    DEFAULT_URLS = [
        "https://google.com",
        "https://github.com",
        "https://httpstat.us/200",
        "https://httpstat.us/503",
    ]

    parser = argparse.ArgumentParser(description="Check HTTP health of URLs.")
    parser.add_argument("--urls", nargs="+", default=None, help="URLs to check")
    parser.add_argument("--file", help="File with one URL per line")
    parser.add_argument(
        "--timeout", type=float, default=5.0, help="Timeout per request (default: 5s)"
    )
    args = parser.parse_args()

    urls = args.urls or []
    if args.file:
        with open(args.file) as f:
            urls += [line.strip() for line in f if line.strip() and not line.startswith("#")]
    if not urls:
        urls = DEFAULT_URLS

    # TODO: Call check_url() for each URL and collect results.
    # BONUS: Use concurrent.futures.ThreadPoolExecutor to check URLs in parallel!
    results = []  # Replace with your logic

    print_report(results, args.timeout)


# ── HINTS ─────────────────────────────────────────────────────────────────────
# 1. urllib.request.urlopen() raises urllib.error.HTTPError for 4xx/5xx responses.
#    HTTPError has a .code attribute with the status code.
# 2. urllib.error.URLError wraps connection errors (DNS failure, refused, timeout).
#    Its .reason attribute contains a human-readable message.
# 3. BONUS: Once working, import ThreadPoolExecutor from concurrent.futures
#    and run checks in parallel — refer to 04_network/ping_hosts.py for an example.
