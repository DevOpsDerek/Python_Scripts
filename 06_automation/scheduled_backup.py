"""
scheduled_backup.py — Run recurring backups on a schedule
==========================================================
Concepts covered:
  - schedule library  (simple job scheduling)
  - logging module    (persistent log of backup activity)
  - datetime          (timestamped filenames)
  - shutil            (creating archives)
  - signal            (graceful shutdown on Ctrl+C / SIGTERM)
  - Functions as first-class objects (passing functions to schedule)
"""

import logging
import shutil
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

import schedule  # pip install schedule


# ---------------------------------------------------------------------------
# Configure logging to write both to the console AND a log file.
# ---------------------------------------------------------------------------
def setup_logging(log_file: str = "backup_scheduler.log") -> None:
    """Set up root logger with a file handler and a stream handler."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file),         # Write to file
            logging.StreamHandler(sys.stdout),     # Also print to terminal
        ],
    )


log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Backup job
# ---------------------------------------------------------------------------
def run_backup(source: str, destination: str, compress: bool = True) -> None:
    """Archive *source* into *destination* with a timestamped filename.

    This function is designed to be passed to schedule.every().do(run_backup, ...).
    The `schedule` library calls it on the configured interval.

    Args:
        source:      Directory to back up.
        destination: Where to store the backup archives.
    """
    src = Path(source)
    dest_dir = Path(destination)

    if not src.exists():
        log.error("Source directory not found: %s", src)
        return

    dest_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_name = f"{src.name}_backup_{timestamp}"
    archive_path = dest_dir / archive_name

    log.info("Starting backup: %s → %s", src, archive_path)
    start = time.time()

    try:
        if compress:
            # shutil.make_archive creates a .tar.gz file
            final_path = shutil.make_archive(
                base_name=str(archive_path),
                format="gztar",
                root_dir=src.parent,
                base_dir=src.name,
            )
        else:
            shutil.copytree(src, archive_path)
            final_path = str(archive_path)

        elapsed = time.time() - start
        size = Path(final_path).stat().st_size / 1_048_576
        log.info("✅ Backup complete: %s  (%.1f MB, %.1fs)", final_path, size, elapsed)

    except Exception as e:
        log.error("❌ Backup failed: %s", e)


# ---------------------------------------------------------------------------
# Graceful shutdown handler
# ---------------------------------------------------------------------------
def install_signal_handlers() -> None:
    """Register handlers for SIGINT (Ctrl+C) and SIGTERM (kill command).

    Without this, the process prints a messy traceback on Ctrl+C.
    """
    def shutdown(signum, frame):
        log.info("Received signal %d — shutting down scheduler.", signum)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(source: str, destination: str, interval: str, compress: bool) -> None:
    """Set up the backup schedule and run the scheduler loop.

    Args:
        source:      Directory to back up.
        destination: Where to store backups.
        interval:    One of: 'hourly', 'daily', 'weekly', or 'NNm' (minutes).
        compress:    Whether to create .tar.gz archives.
    """
    setup_logging()
    install_signal_handlers()

    # Schedule the backup job based on the requested interval.
    # schedule.every().hour.do(fn) registers fn to run each hour.
    if interval == "hourly":
        schedule.every().hour.do(run_backup, source, destination, compress)
        desc = "every hour"
    elif interval == "daily":
        schedule.every().day.at("02:00").do(run_backup, source, destination, compress)
        desc = "daily at 02:00"
    elif interval == "weekly":
        schedule.every().monday.at("03:00").do(run_backup, source, destination, compress)
        desc = "every Monday at 03:00"
    elif interval.endswith("m"):
        minutes = int(interval[:-1])
        schedule.every(minutes).minutes.do(run_backup, source, destination, compress)
        desc = f"every {minutes} minutes"
    else:
        log.error("Unknown interval: %s. Use: hourly, daily, weekly, or NNm (e.g. 30m)", interval)
        sys.exit(1)

    log.info("Scheduler started — backing up '%s' to '%s' (%s)", source, destination, desc)
    log.info("Press Ctrl+C to stop.")

    # Run once immediately on startup so we don't wait for the first interval
    run_backup(source, destination, compress)

    # The main scheduler loop — schedule.run_pending() triggers any due jobs
    while True:
        schedule.run_pending()
        next_run = schedule.next_run()
        if next_run:
            wait = (next_run - datetime.now()).total_seconds()
            log.info("Next backup in %.0f seconds (at %s)", wait, next_run.strftime("%H:%M:%S"))
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run automated backups on a schedule.")
    parser.add_argument("source", help="Directory to back up")
    parser.add_argument("destination", help="Destination for backup archives")
    parser.add_argument(
        "-i", "--interval",
        default="daily",
        help="Schedule: hourly, daily, weekly, or NNm (e.g. 30m). Default: daily",
    )
    parser.add_argument("--no-compress", dest="compress", action="store_false", default=True,
                        help="Copy directory instead of creating .tar.gz")
    args = parser.parse_args()

    main(args.source, args.destination, args.interval, args.compress)

# ---------------------------------------------------------------------------
# TRY THIS:
#   python scheduled_backup.py ~/Documents ~/Backups --interval 5m
#   python scheduled_backup.py ~/Documents ~/Backups --interval daily
#   python scheduled_backup.py ~/Documents ~/Backups --no-compress
# ---------------------------------------------------------------------------
