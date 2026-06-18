"""
cpu_monitor.py — Real-time CPU usage monitor with per-core breakdown
====================================================================
Concepts covered:
  - psutil         (CPU metrics)
  - time.sleep()   (polling intervals)
  - ANSI escape codes (clearing the terminal for live refresh)
  - KeyboardInterrupt (graceful Ctrl+C handling)
  - Collections.deque (rolling window / circular buffer)
"""

from collections import deque
from datetime import datetime

import psutil  # pip install psutil

# ANSI escape code to move the cursor to the top-left of the terminal.
# This lets us "redraw" the screen in place rather than scrolling endlessly.
CURSOR_HOME = "\033[H"
CLEAR_SCREEN = "\033[2J"


def render_bar(percent: float, width: int = 25) -> str:
    """Draw a coloured ASCII bar using ANSI colour codes.

    Colour logic:
      Green  (low load):   0 – 60 %
      Yellow (medium):    61 – 80 %
      Red    (high load): 81 – 100 %
    """
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)

    if percent <= 60:
        colour = "\033[92m"  # Bright green
    elif percent <= 80:
        colour = "\033[93m"  # Bright yellow
    else:
        colour = "\033[91m"  # Bright red

    reset = "\033[0m"
    return f"{colour}[{bar}]{reset} {percent:5.1f}%"


def monitor_cpu(interval: float = 1.0, history_len: int = 60) -> None:
    """Continuously display CPU usage until the user presses Ctrl+C.

    Args:
        interval:    Seconds between refreshes.
        history_len: How many samples to keep for the mini sparkline graph.
    """
    # deque with maxlen acts as a circular buffer — old values drop off automatically
    history: deque = deque(maxlen=history_len)

    print(CLEAR_SCREEN, end="")  # Clear screen once at startup

    try:
        while True:
            # cpu_percent(percpu=True) returns a list, one value per logical core
            per_core = psutil.cpu_percent(interval=interval, percpu=True)
            total = psutil.cpu_percent(interval=None)  # Instant read (no sleep)
            freq = psutil.cpu_freq()
            load_avg = psutil.getloadavg() if hasattr(psutil, "getloadavg") else (0, 0, 0)

            history.append(total)

            # Move cursor back to top-left to "redraw" in place
            print(CURSOR_HOME, end="")

            now = datetime.now().strftime("%H:%M:%S")
            print(f"\n  🖥️  CPU Monitor  —  {now}  (Ctrl+C to exit)\n")
            print(f"  {'─' * 55}")

            # --- Overall ---
            print(f"  Overall      {render_bar(total)}")

            if freq:
                print(f"  Frequency    {freq.current:,.0f} MHz  (max: {freq.max:,.0f} MHz)")

            if hasattr(psutil, "getloadavg"):
                print(
                    f"  Load avg     {load_avg[0]:.2f}  {load_avg[1]:.2f}  {load_avg[2]:.2f}  (1m / 5m / 15m)"
                )

            # --- Per-core ---
            print(f"\n  {'─' * 55}")
            for i, pct in enumerate(per_core):
                print(f"  Core {i:<4}    {render_bar(pct, width=20)}")

            # --- History sparkline ---
            # Map each sample to a Braille block character for a tiny graph
            SPARK_CHARS = " ▁▂▃▄▅▆▇█"
            spark = "".join(
                SPARK_CHARS[min(int(v / 100 * (len(SPARK_CHARS) - 1)), len(SPARK_CHARS) - 1)]
                for v in history
            )
            print(f"\n  {'─' * 55}")
            print(f"  History ({len(history)}s)  {spark}")
            print(f"  {'─' * 55}\n")

            # Clear any leftover lines from a previous draw that had more cores
            # (handles terminal resize)
            print("\033[J", end="", flush=True)

    except KeyboardInterrupt:
        # This exception is raised when the user presses Ctrl+C.
        # We catch it to print a clean exit message instead of a traceback.
        print("\n\n  Monitoring stopped.\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Real-time CPU usage monitor.")
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=1.0,
        help="Refresh interval in seconds (default: 1.0)",
    )
    args = parser.parse_args()

    monitor_cpu(interval=args.interval)

# ---------------------------------------------------------------------------
# TRY THIS:
#   python cpu_monitor.py              # refresh every second
#   python cpu_monitor.py -i 0.5      # refresh every 0.5 seconds
#   # Open another terminal and run: stress --cpu 4  (if stress is installed)
#   # to see the graph respond to load
# ---------------------------------------------------------------------------
