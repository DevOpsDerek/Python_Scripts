"""Tests for exercises/*/solution.py files.

We test the solution files (not the exercise stubs) since those contain
the complete working implementations.
"""

import os
from pathlib import Path

from tests.conftest import load_script

ex01 = load_script("exercises/01_file_extension_report/solution.py")
ex02 = load_script("exercises/02_find_files/solution.py")
ex03 = load_script("exercises/03_disk_alert/solution.py")
ex04 = load_script("exercises/04_process_watchdog/solution.py")
ex05 = load_script("exercises/05_http_health_checker/solution.py")
ex06 = load_script("exercises/06_log_grepper/solution.py")
ex07 = load_script("exercises/07_uptime_logger/solution.py")
ex08 = load_script("exercises/08_env_inspector/solution.py")
ex09 = load_script("exercises/09_dir_size_report/solution.py")
ex10 = load_script("exercises/10_health_snapshot/solution.py")


# ── Exercise 01: File Extension Report ────────────────────────────────────────


class TestEx01FileExtensionReport:
    def test_get_extension_with_suffix(self, tmp_path):
        f = tmp_path / "report.pdf"
        f.touch()
        assert ex01.get_extension(f) == ".pdf"

    def test_get_extension_lowercases(self, tmp_path):
        f = tmp_path / "IMAGE.PNG"
        f.touch()
        assert ex01.get_extension(f) == ".png"

    def test_get_extension_no_suffix(self, tmp_path):
        f = tmp_path / "Makefile"
        f.touch()
        assert ex01.get_extension(f) == "(no ext)"

    def test_count_extensions_groups_correctly(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        (tmp_path / "c.py").write_text("c")
        counts = ex01.count_extensions(str(tmp_path))
        assert counts[".txt"] == 2
        assert counts[".py"] == 1

    def test_render_bar_scales_proportionally(self):
        full = ex01.render_bar(100, 100, width=10)
        half = ex01.render_bar(50, 100, width=10)
        assert len(full) == 10
        assert len(half) == 5

    def test_print_report_output(self, tmp_path, capsys):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.py").write_text("b")
        from collections import Counter

        counts = Counter({".txt": 3, ".py": 1})
        ex01.print_report(str(tmp_path), counts)
        out = capsys.readouterr().out
        assert ".txt" in out
        assert ".py" in out


# ── Exercise 02: Find Files ────────────────────────────────────────────────────


class TestEx02FindFiles:
    def test_finds_matching_files(self, tmp_path):
        (tmp_path / "hello.py").write_text("x")
        (tmp_path / "world.py").write_text("x")
        (tmp_path / "readme.txt").write_text("x")
        results = list(ex02.find_files(str(tmp_path), "*.py"))
        names = [r.name for r in results]
        assert "hello.py" in names
        assert "world.py" in names
        assert "readme.txt" not in names

    def test_no_match_returns_empty(self, tmp_path):
        (tmp_path / "file.txt").write_text("x")
        results = list(ex02.find_files(str(tmp_path), "*.xyz"))
        assert results == []

    def test_invalid_directory_yields_nothing(self):
        results = list(ex02.find_files("/nonexistent/path/xyz", "*.py"))
        assert results == []

    def test_format_size_bytes(self):
        assert ex02.format_size(500) == "500 B"

    def test_format_size_kilobytes(self):
        assert "KB" in ex02.format_size(2048)


# ── Exercise 03: Disk Alert ────────────────────────────────────────────────────


class TestEx03DiskAlert:
    def test_check_disk_returns_dict_with_required_keys(self):
        result = ex03.check_disk("/", threshold=80.0)
        assert result is not None
        for key in ("mount", "total_gb", "used_gb", "free_gb", "percent", "alert"):
            assert key in result

    def test_check_disk_alert_true_when_above_threshold(self):
        result = ex03.check_disk("/", threshold=0.0)  # 0% threshold → always alerts
        assert result["alert"] is True

    def test_check_disk_alert_false_when_below_threshold(self):
        result = ex03.check_disk("/", threshold=100.0)  # 100% threshold → never alerts
        assert result["alert"] is False

    def test_print_report_returns_zero_when_clean(self, capsys):
        results = [ex03.check_disk("/", threshold=100.0)]
        code = ex03.print_report(results, threshold=100.0)
        capsys.readouterr()
        assert code == 0

    def test_print_report_returns_one_when_alert(self, capsys):
        results = [ex03.check_disk("/", threshold=0.0)]
        code = ex03.print_report(results, threshold=0.0)
        capsys.readouterr()
        assert code == 1


# ── Exercise 04: Process Watchdog ─────────────────────────────────────────────


class TestEx04ProcessWatchdog:
    def test_finds_running_python_process(self):
        running, pid = ex04.is_process_running("python")
        assert running is True
        assert pid is not None

    def test_nonexistent_process_not_found(self):
        running, pid = ex04.is_process_running("zzz_no_such_proc_xyz_999")
        assert running is False
        assert pid is None


# ── Exercise 05: HTTP Health Checker ──────────────────────────────────────────


class TestEx05HttpHealthChecker:
    def test_check_url_returns_check_result(self):
        result = ex05.check_url("https://httpstat.us/200", timeout=10.0)
        # httpstat.us/200 always returns 200, but we just check structure
        assert hasattr(result, "url")
        assert hasattr(result, "status")
        assert hasattr(result, "elapsed_s")

    def test_invalid_url_returns_error(self):
        result = ex05.check_url("https://this.invalid.hostname.xyz", timeout=3.0)
        assert result.status is None
        assert result.error != ""

    def test_elapsed_is_positive(self):
        result = ex05.check_url("https://this.invalid.hostname.xyz", timeout=2.0)
        assert result.elapsed_s >= 0


# ── Exercise 06: Log Grepper ───────────────────────────────────────────────────


class TestEx06LogGrepper:
    def test_finds_matching_lines(self, sample_log):
        matches = list(ex06.grep_file(sample_log, "ERROR", ignore_case=False))
        assert len(matches) == 2
        for line_no, line in matches:
            assert "ERROR" in line

    def test_case_insensitive_search(self, sample_log):
        lower = list(ex06.grep_file(sample_log, "error", ignore_case=True))
        upper = list(ex06.grep_file(sample_log, "ERROR", ignore_case=False))
        assert len(lower) == len(upper)

    def test_no_match_yields_nothing(self, sample_log):
        matches = list(ex06.grep_file(sample_log, "ZZZNOTINLOG", ignore_case=False))
        assert matches == []

    def test_find_log_files_single_file(self, sample_log):
        files = ex06.find_log_files(str(sample_log), [".log"])
        assert len(files) == 1

    def test_find_log_files_directory(self, tmp_path):
        (tmp_path / "a.log").write_text("log a")
        (tmp_path / "b.log").write_text("log b")
        (tmp_path / "c.txt").write_text("not a log")
        files = ex06.find_log_files(str(tmp_path), [".log"])
        assert len(files) == 2


# ── Exercise 07: Uptime Logger ────────────────────────────────────────────────


class TestEx07UptimeLogger:
    def test_collect_sample_has_required_keys(self):
        sample = ex07.collect_sample()
        for key in ("timestamp", "cpu_pct", "mem_pct", "disk_pct"):
            assert key in sample

    def test_cpu_pct_in_valid_range(self):
        sample = ex07.collect_sample()
        assert 0.0 <= sample["cpu_pct"] <= 100.0

    def test_write_sample_creates_csv(self, tmp_path):
        csv_file = str(tmp_path / "test.csv")
        sample = ex07.collect_sample()
        ex07.write_sample(csv_file, sample, write_header=True)
        content = Path(csv_file).read_text()
        assert "timestamp" in content
        assert "cpu_pct" in content

    def test_write_sample_appends(self, tmp_path):
        csv_file = str(tmp_path / "test.csv")
        sample = ex07.collect_sample()
        ex07.write_sample(csv_file, sample, write_header=True)
        ex07.write_sample(csv_file, sample, write_header=False)
        lines = Path(csv_file).read_text().strip().splitlines()
        assert len(lines) == 3  # 1 header + 2 data rows


# ── Exercise 08: Environment Inspector ───────────────────────────────────────


class TestEx08EnvInspector:
    def test_returns_all_vars_when_no_filter(self):
        results = ex08.get_env_vars()
        assert len(results) == len(os.environ)

    def test_prefix_filter_works(self):
        os.environ["TEST_EX08_PREFIX_VAR"] = "value"
        results = ex08.get_env_vars(prefix="TEST_EX08")
        names = [n for n, _ in results]
        assert "TEST_EX08_PREFIX_VAR" in names
        del os.environ["TEST_EX08_PREFIX_VAR"]

    def test_search_filter_finds_in_value(self):
        os.environ["TEST_EX08_SEARCH"] = "unique_sentinel_value_xyz"
        results = ex08.get_env_vars(search="unique_sentinel_value_xyz")
        names = [n for n, _ in results]
        assert "TEST_EX08_SEARCH" in names
        del os.environ["TEST_EX08_SEARCH"]

    def test_results_are_sorted_alphabetically(self):
        results = ex08.get_env_vars()
        names = [n.lower() for n, _ in results]
        assert names == sorted(names)

    def test_truncate_short_string_unchanged(self):
        assert ex08.truncate("hello", 10) == "hello"

    def test_truncate_long_string_shortened(self):
        result = ex08.truncate("hello world", 8)
        assert len(result) == 8
        assert result.endswith("…")


# ── Exercise 09: Directory Size Report ────────────────────────────────────────


class TestEx09DirSizeReport:
    def test_get_dir_size_returns_tuple(self, tmp_path):
        (tmp_path / "a.txt").write_bytes(b"x" * 1000)
        size, count = ex09.get_dir_size(tmp_path)
        assert isinstance(size, int)
        assert isinstance(count, int)

    def test_get_dir_size_counts_files(self, tmp_path):
        (tmp_path / "a.txt").write_bytes(b"x" * 100)
        (tmp_path / "b.txt").write_bytes(b"x" * 200)
        size, count = ex09.get_dir_size(tmp_path)
        assert count == 2
        assert size == 300

    def test_bytes_to_human_b(self):
        assert "B" in ex09.bytes_to_human(500)

    def test_bytes_to_human_gb(self):
        assert "GB" in ex09.bytes_to_human(1024**3)

    def test_report_runs_without_error(self, tmp_path, capsys):
        subdir = tmp_path / "mydir"
        subdir.mkdir()
        (subdir / "file.txt").write_bytes(b"x" * 100)
        ex09.report(str(tmp_path), top_n=0)
        out = capsys.readouterr().out
        assert "mydir" in out


# ── Exercise 10: System Health Snapshot ───────────────────────────────────────


class TestEx10HealthSnapshot:
    def test_collect_cpu_has_required_keys(self):
        cpu = ex10.collect_cpu()
        for key in ("percent", "cores_physical", "cores_logical", "freq_mhz"):
            assert key in cpu

    def test_collect_memory_has_required_keys(self):
        mem = ex10.collect_memory()
        for key in ("total_gb", "used_gb", "available_gb", "percent"):
            assert key in mem

    def test_collect_disk_is_non_empty_dict(self):
        disk = ex10.collect_disk()
        assert isinstance(disk, dict)
        assert len(disk) >= 1

    def test_build_snapshot_structure(self):
        snap = ex10.build_snapshot()
        for key in ("generated_at", "hostname", "cpu", "memory", "disk", "top_processes"):
            assert key in snap

    def test_save_and_load_snapshot(self, tmp_path):
        snap = ex10.build_snapshot()
        saved = ex10.save_snapshot(snap, str(tmp_path))
        assert saved.exists()
        loaded = ex10.load_latest_snapshot(str(tmp_path))
        assert loaded is not None
        assert loaded["hostname"] == snap["hostname"]

    def test_top_processes_is_list(self):
        procs = ex10.collect_top_processes(top_n=3)
        assert isinstance(procs, list)
        assert len(procs) <= 3
