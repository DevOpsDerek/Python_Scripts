"""
Exercise 05 — HTTP Health Checker  ✅ SOLUTION
"""

import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional


@dataclass
class CheckResult:
    url: str
    status: Optional[int]
    elapsed_s: float
    error: str = ""


def check_url(url: str, timeout: float = 5.0) -> CheckResult:
    start = time.time()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            status = resp.status
        return CheckResult(url=url, status=status, elapsed_s=time.time() - start)
    except urllib.error.HTTPError as e:
        return CheckResult(url=url, status=e.code, elapsed_s=time.time() - start,
                           error=str(e.reason))
    except urllib.error.URLError as e:
        return CheckResult(url=url, status=None, elapsed_s=time.time() - start,
                           error=str(e.reason))
    except Exception as e:
        return CheckResult(url=url, status=None, elapsed_s=time.time() - start,
                           error=str(e))


def print_report(results: list, timeout: float) -> None:
    print(f"\n  HTTP Health Check  (timeout: {timeout}s)")
    print("  " + "─" * 60)

    healthy = 0
    for r in results:
        elapsed = f"({r.elapsed_s:.2f}s)"
        if r.status == 200:
            icon = "✅"
            status_str = f"\033[92m{r.status}\033[0m"
            healthy += 1
        elif r.status:
            icon = "⚠️ "
            status_str = f"\033[93m{r.status}\033[0m"
        else:
            icon = "❌"
            status_str = "\033[91mERR\033[0m"

        note = f"  {r.error[:30]}" if r.error and not r.status else ""
        print(f"  {icon}  {status_str:<16}  {r.url:<45} {elapsed}{note}")

    print(f"\n  {healthy}/{len(results)} healthy\n")


if __name__ == "__main__":
    import argparse

    DEFAULT_URLS = [
        "https://google.com",
        "https://github.com",
        "https://httpstat.us/200",
        "https://httpstat.us/503",
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", nargs="+", default=None)
    parser.add_argument("--file", default=None)
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    urls = args.urls or []
    if args.file:
        with open(args.file) as f:
            urls += [line.strip() for line in f if line.strip() and not line.startswith("#")]
    if not urls:
        urls = DEFAULT_URLS

    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(check_url, u, args.timeout): u for u in urls}
        results = [f.result() for f in as_completed(futures)]

    results.sort(key=lambda r: urls.index(r.url))
    print_report(results, args.timeout)
