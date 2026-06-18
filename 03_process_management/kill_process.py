"""
kill_process.py — Safely terminate processes by name or PID
===========================================================
Concepts covered:
  - psutil.Process.terminate() vs .kill() (graceful vs forced)
  - Signal handling concepts (SIGTERM, SIGKILL)
  - User confirmation prompts (input())
  - Error handling: NoSuchProcess, AccessDenied, TimeoutExpired
  - Safety patterns: dry-run mode, confirmation, protected list
"""

from __future__ import annotations

import time

import psutil  # pip install psutil

# ---------------------------------------------------------------------------
# Protected process names — we refuse to kill these to prevent accidents.
# Expand this list based on your environment.
# ---------------------------------------------------------------------------
PROTECTED_NAMES = {
    "init",
    "systemd",
    "launchd",
    "kernel_task",
    "sshd",
    "login",
    "python",  # Don't kill your own interpreter!
}


def find_by_pid(pid: int) -> psutil.Process | None:
    """Return a Process object for the given PID, or None if not found."""
    try:
        return psutil.Process(pid)
    except psutil.NoSuchProcess:
        return None


def find_by_name(name: str) -> list:
    """Return all processes whose name contains *name* (case-insensitive)."""
    matches = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if name.lower() in (proc.info["name"] or "").lower():
                matches.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return matches


def is_protected(proc: psutil.Process) -> bool:
    """Return True if the process name is on the protected list."""
    try:
        return proc.name().lower() in PROTECTED_NAMES
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def terminate_process(
    proc: psutil.Process,
    force: bool = False,
    timeout: float = 5.0,
    dry_run: bool = False,
) -> bool:
    """Attempt to terminate a process gracefully (SIGTERM), then forcefully (SIGKILL).

    The two-step approach:
      1. Send SIGTERM — asks the process to shut down cleanly (it can ignore this).
      2. Wait `timeout` seconds for the process to exit.
      3. If still running, send SIGKILL — cannot be ignored, immediately terminates.

    Args:
        proc:    The process to terminate.
        force:   If True, skip SIGTERM and go straight to SIGKILL.
        timeout: Seconds to wait after SIGTERM before escalating to SIGKILL.
        dry_run: If True, print what would happen but don't actually do anything.

    Returns:
        True if the process was terminated, False otherwise.
    """
    try:
        name = proc.name()
        pid = proc.pid
    except psutil.NoSuchProcess:
        print("  ℹ️  Process already gone.")
        return True

    if is_protected(proc):
        print(f"  ⛔  Refusing to kill protected process: {name} (PID {pid})")
        return False

    if dry_run:
        print(f"  [DRY RUN] Would terminate: {name} (PID {pid})")
        return True

    try:
        if force:
            print(f"  ⚡  Sending SIGKILL to {name} (PID {pid})…")
            proc.kill()  # SIGKILL — immediate, brutal, unblockable
        else:
            print(f"  ✉️   Sending SIGTERM to {name} (PID {pid})…")
            proc.terminate()  # SIGTERM — polite request to stop

            # Wait for the process to exit on its own
            proc.wait(timeout=timeout)
            print(f"  ✅  {name} (PID {pid}) terminated gracefully.")
            return True

    except psutil.TimeoutExpired:
        # Process didn't respond to SIGTERM in time — escalate to SIGKILL
        print(f"  ⚠️   {name} didn't stop within {timeout}s. Escalating to SIGKILL…")
        try:
            proc.kill()
        except psutil.NoSuchProcess:
            pass  # Process died in the meantime — that's fine

    except psutil.AccessDenied:
        print(f"  ❌  Permission denied: cannot kill {name} (PID {pid}).")
        print("      Try running with sudo.")
        return False

    except psutil.NoSuchProcess:
        print(f"  ℹ️   {name} (PID {pid}) already exited.")
        return True

    # Verify it's gone
    time.sleep(0.3)
    if not psutil.pid_exists(pid):
        print(f"  ✅  {name} (PID {pid}) is gone.")
        return True
    else:
        print(f"  ❌  {name} (PID {pid}) is still running!")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Terminate processes by PID or name.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pid", type=int, help="Terminate process with this PID")
    group.add_argument("--name", help="Terminate all processes matching this name")
    parser.add_argument("--force", action="store_true", help="Use SIGKILL instead of SIGTERM")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be killed, without doing it"
    )
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    if args.pid:
        proc = find_by_pid(args.pid)
        if not proc:
            print(f"\n  ❌ No process found with PID {args.pid}\n")
            raise SystemExit(1)
        targets = [proc]
    else:
        targets = find_by_name(args.name)
        if not targets:
            print(f"\n  ❌ No processes found matching '{args.name}'\n")
            raise SystemExit(1)

    # Confirm before doing anything destructive
    print("\n  Processes to be terminated:")
    for p in targets:
        try:
            print(f"    PID {p.pid}  {p.name()}  [{p.status()}]")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if not args.dry_run and not args.yes:
        answer = input(f"\n  Terminate {len(targets)} process(es)? [y/N] ").strip().lower()
        if answer != "y":
            print("  Aborted.\n")
            raise SystemExit(0)

    print()
    for proc in targets:
        terminate_process(proc, force=args.force, dry_run=args.dry_run)

    print()

# ---------------------------------------------------------------------------
# TRY THIS:
#   python kill_process.py --name sleep --dry-run  # safe preview
#   python kill_process.py --pid 12345
#   python kill_process.py --name myapp --force
# ---------------------------------------------------------------------------
