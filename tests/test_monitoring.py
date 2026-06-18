"""Tests for 02_system_monitoring scripts."""

from tests.conftest import load_script

si = load_script("02_system_monitoring/system_info.py")
du = load_script("02_system_monitoring/disk_usage.py")
mm = load_script("02_system_monitoring/memory_monitor.py")


# ── system_info ────────────────────────────────────────────────────────────────


class TestCollectSystemInfo:
    def test_returns_snapshot_object(self):
        snap = si.collect_system_info()
        assert isinstance(snap, si.SystemSnapshot)

    def test_hostname_is_non_empty_string(self):
        snap = si.collect_system_info()
        assert isinstance(snap.hostname, str)
        assert len(snap.hostname) > 0

    def test_cpu_core_count_is_positive(self):
        snap = si.collect_system_info()
        assert snap.cpu_cores_logical >= 1
        assert snap.cpu_cores_physical >= 1

    def test_ram_total_is_positive(self):
        snap = si.collect_system_info()
        assert snap.ram_total_gb > 0

    def test_ram_percent_in_valid_range(self):
        snap = si.collect_system_info()
        assert 0.0 <= snap.ram_percent <= 100.0

    def test_disk_info_is_dict(self):
        snap = si.collect_system_info()
        assert isinstance(snap.disk_info, dict)

    def test_uptime_is_positive(self):
        snap = si.collect_system_info()
        assert snap.uptime.total_seconds() > 0


class TestRenderBar:
    def test_zero_percent_is_all_empty(self):
        bar = si.render_bar(0, width=10)
        assert "█" not in bar
        assert "░" * 10 in bar

    def test_hundred_percent_is_all_filled(self):
        bar = si.render_bar(100, width=10)
        assert "█" * 10 in bar
        assert "░" not in bar

    def test_fifty_percent_is_half_filled(self):
        bar = si.render_bar(50, width=10)
        assert bar.count("█") == 5
        assert bar.count("░") == 5

    def test_bar_contains_percentage(self):
        bar = si.render_bar(75)
        assert "75.0%" in bar


# ── disk_usage ─────────────────────────────────────────────────────────────────


class TestDiskUsage:
    def test_bytes_to_human_bytes(self):
        assert du.bytes_to_human(500) == "500.0 B"

    def test_bytes_to_human_mb(self):
        result = du.bytes_to_human(1024 * 1024)
        assert "MB" in result

    def test_bytes_to_human_gb(self):
        result = du.bytes_to_human(1024**3)
        assert "GB" in result

    def test_show_disk_usage_runs_without_error(self, capsys):
        du.show_disk_usage()
        out = capsys.readouterr().out
        # Should print at least one partition
        assert "DISK USAGE" in out.upper() or "/" in out


# ── memory_monitor ─────────────────────────────────────────────────────────────


class TestMemoryMonitor:
    def test_bytes_to_human_formats_correctly(self):
        assert mm.bytes_to_human(0) == "0.0 B"
        assert "KB" in mm.bytes_to_human(2048)
        assert "MB" in mm.bytes_to_human(1024 * 1024 * 5)

    def test_show_memory_runs_without_error(self, capsys):
        mm.show_memory()
        out = capsys.readouterr().out
        assert "MEMORY" in out.upper()

    def test_show_top_memory_processes_runs(self, capsys):
        mm.show_top_memory_processes(top_n=3)
        out = capsys.readouterr().out
        # Should show at least the header
        assert "MEMORY" in out.upper() or "PID" in out
