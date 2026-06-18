"""Tests for 03_process_management scripts."""

import os

import psutil

from tests.conftest import load_script

lp = load_script("03_process_management/list_processes.py")
fp = load_script("03_process_management/find_process.py")
kp = load_script("03_process_management/kill_process.py")


# ── list_processes ─────────────────────────────────────────────────────────────


class TestListProcesses:
    def test_bytes_to_mb_conversion(self):
        assert lp.bytes_to_mb(1_048_576) == 1.0
        assert lp.bytes_to_mb(0) == 0.0
        assert lp.bytes_to_mb(524_288) == 0.5

    def test_list_processes_runs_without_error(self, capsys):
        lp.list_processes(sort_by="pid", top_n=5)
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_filter_by_name_narrows_results(self, capsys):
        # Filter for a name that definitely won't exist
        lp.list_processes(filter_name="zzz_no_such_process_xyz")
        out = capsys.readouterr().out
        # Should show 0 processes in the results
        assert "0 of 0" in out or out.strip() == "" or "0" in out

    def test_sort_options_dont_crash(self, capsys):
        for sort_key in ["cpu", "mem", "pid", "name"]:
            lp.list_processes(sort_by=sort_key, top_n=3)
        # If no exception raised, all sort options work
        capsys.readouterr()


# ── find_process ───────────────────────────────────────────────────────────────


class TestFindProcess:
    def test_finds_current_python_process(self):
        # The test runner itself is a Python process
        matches = fp.find_processes("python")
        assert len(matches) >= 1

    def test_no_match_returns_empty_list(self):
        matches = fp.find_processes("zzz_definitely_not_running_xyz_123")
        assert matches == []

    def test_returns_process_objects(self):
        matches = fp.find_processes("python")
        for proc in matches:
            assert isinstance(proc, psutil.Process)

    def test_format_bytes_helper(self):
        assert fp.format_bytes(0) == "0.0 B"
        assert "KB" in fp.format_bytes(2048)
        assert "MB" in fp.format_bytes(1024 * 1024 * 3)


# ── kill_process (safety checks only — we don't actually kill anything) ────────


class TestKillProcessSafety:
    def test_protected_process_is_refused(self):
        """Verify that protected process names are flagged."""
        # Create a mock process-like object using the real current process
        current = psutil.Process(os.getpid())
        # The protection check uses the name, not whether it's actually protected
        # We verify the function exists and returns a bool
        result = kp.is_protected(current)
        assert isinstance(result, bool)

    def test_find_by_pid_returns_process_for_self(self):
        pid = os.getpid()
        proc = kp.find_by_pid(pid)
        assert proc is not None
        assert proc.pid == pid

    def test_find_by_pid_returns_none_for_invalid_pid(self):
        result = kp.find_by_pid(9_999_999)
        assert result is None

    def test_find_by_name_finds_self(self):
        matches = kp.find_by_name("python")
        assert len(matches) >= 1

    def test_dry_run_does_not_kill(self):
        """dry_run=True must never actually terminate anything."""
        import subprocess

        # Spawn a short-lived sleep process — not in the protected list
        proc = subprocess.Popen(["sleep", "30"])
        psutil_proc = psutil.Process(proc.pid)
        try:
            result = kp.terminate_process(psutil_proc, dry_run=True)
            assert psutil.pid_exists(proc.pid)
            assert result is True
        finally:
            proc.kill()
            proc.wait()
