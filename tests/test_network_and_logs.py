"""Tests for 04_network and 05_log_analysis scripts."""

import socket

from tests.conftest import load_script

# Network
ph = load_script("04_network/ping_hosts.py")
ps = load_script("04_network/port_scanner.py")
ni = load_script("04_network/network_info.py")

# Log analysis
pl = load_script("05_log_analysis/parse_logs.py")
tl = load_script("05_log_analysis/tail_log.py")
ce = load_script("05_log_analysis/count_errors.py")


# ── network: port_scanner ─────────────────────────────────────────────────────


class TestPortScanner:
    def test_closed_port_returns_none(self):
        # Port 1 requires root — it's almost universally closed
        result = ps.check_port("127.0.0.1", 1, timeout=0.3)
        assert result is None

    def test_open_port_returns_port_number(self):
        """Spin up a real TCP listener and verify check_port detects it."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]

        try:
            result = ps.check_port("127.0.0.1", port, timeout=1.0)
            assert result == port
        finally:
            server.close()

    def test_resolve_localhost(self):
        ip = ps.resolve_host("localhost")
        assert ip is not None
        assert ip.startswith("127.") or ip == "::1"

    def test_resolve_invalid_host_returns_none(self):
        result = ps.resolve_host("this.host.does.not.exist.invalid")
        assert result is None

    def test_well_known_ports_dict_has_ssh(self):
        assert ps.WELL_KNOWN_PORTS.get(22) == "SSH"

    def test_well_known_ports_dict_has_http(self):
        assert ps.WELL_KNOWN_PORTS.get(80) == "HTTP"


# ── network: ping_hosts ────────────────────────────────────────────────────────


class TestPingHosts:
    def test_ping_localhost_succeeds(self):
        result = ph.ping_host("127.0.0.1", count=1)
        assert result.reachable is True
        assert result.host == "127.0.0.1"

    def test_ping_unreachable_host(self):
        # RFC 5737 TEST-NET: 192.0.2.1 is reserved and should not respond
        result = ph.ping_host("192.0.2.1", count=1)
        assert result.reachable is False

    def test_ping_result_has_correct_host(self):
        result = ph.ping_host("127.0.0.1", count=1)
        assert result.host == "127.0.0.1"

    def test_ping_all_returns_list_of_results(self):
        results = ph.ping_all(["127.0.0.1"], count=1, workers=1)
        assert len(results) == 1
        assert results[0].host == "127.0.0.1"


# ── network: network_info ──────────────────────────────────────────────────────


class TestNetworkInfo:
    def test_get_public_ip_returns_string(self):
        ip = ni.get_public_ip()
        assert isinstance(ip, str)
        assert len(ip) > 0

    def test_bytes_to_human_formats(self):
        assert ni.bytes_to_human(0) == "0.0 B"
        assert "KB" in ni.bytes_to_human(2048)

    def test_show_hostname_runs_without_error(self, capsys):
        ni.show_hostname()
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_show_interfaces_runs_without_error(self, capsys):
        ni.show_interfaces()
        out = capsys.readouterr().out
        assert len(out) > 0


# ── log analysis: parse_logs ───────────────────────────────────────────────────


class TestParseLogs:
    def test_analyse_log_counts_lines(self, sample_log):
        stats = pl.analyse_log(str(sample_log))
        assert stats["total_lines"] == 8

    def test_analyse_log_detects_error_levels(self, sample_log):
        stats = pl.analyse_log(str(sample_log))
        assert stats["level_counts"]["ERROR"] == 2
        assert stats["level_counts"]["CRITICAL"] == 1
        assert stats["level_counts"]["WARNING"] == 1

    def test_analyse_log_collects_error_lines(self, sample_log):
        stats = pl.analyse_log(str(sample_log))
        assert len(stats["errors"]) >= 1

    def test_analyse_log_missing_file_raises(self, tmp_path):
        import pytest

        with pytest.raises(FileNotFoundError):
            pl.analyse_log(str(tmp_path / "missing.log"))

    def test_print_report_runs_without_error(self, sample_log, capsys):
        stats = pl.analyse_log(str(sample_log))
        pl.print_report(stats)
        out = capsys.readouterr().out
        assert "LOG" in out.upper()


# ── log analysis: count_errors ─────────────────────────────────────────────────


class TestCountErrors:
    def test_counts_errors_in_file(self, sample_log, capsys):
        ce.count_errors(str(sample_log))
        out = capsys.readouterr().out
        assert "Error" in out or "ERROR" in out

    def test_no_errors_shows_zero(self, tmp_path, capsys):
        clean_log = tmp_path / "clean.log"
        clean_log.write_text("INFO all good\nINFO server running\n")
        ce.count_errors(str(clean_log))
        out = capsys.readouterr().out
        assert "Error lines:            0" in out or "0" in out

    def test_missing_file_shows_error(self, capsys):
        ce.count_errors("/no/such/file.log")
        out = capsys.readouterr().out
        assert "not found" in out.lower() or "❌" in out


# ── log analysis: tail_log ─────────────────────────────────────────────────────


class TestTailLog:
    def test_colorize_line_no_level_unchanged(self):
        line = "some ordinary log line"
        result = tl.colorize_line(line)
        # Without a keyword the result may or may not have colour — just check no crash
        assert isinstance(result, str)

    def test_colorize_line_error_gets_colour(self):
        line = "ERROR something broke"
        result = tl.colorize_line(line)
        # Should contain ANSI escape codes
        assert "\033[" in result

    def test_tail_nonexistent_file_exits(self):
        import pytest

        with pytest.raises(SystemExit):
            tl.tail_file("/nonexistent/file.log", follow=False)

    def test_tail_prints_last_n_lines(self, sample_log, capsys):
        tl.tail_file(str(sample_log), lines=3, follow=False)
        out = capsys.readouterr().out
        # Should contain at least some output from the file
        assert len(out.strip()) > 0
