"""Tests for 01_filesystem scripts."""

from tests.conftest import load_script

# ── load modules once ──────────────────────────────────────────────────────────
lf = load_script("01_filesystem/list_files.py")
fl = load_script("01_filesystem/find_large_files.py")
fd = load_script("01_filesystem/find_duplicates.py")
bf = load_script("01_filesystem/backup_files.py")


# ── format_size ────────────────────────────────────────────────────────────────


class TestFormatSize:
    def test_bytes(self):
        assert lf.format_size(500) == "500.0 B"

    def test_kilobytes(self):
        assert lf.format_size(1024) == "1.0 KB"

    def test_megabytes(self):
        assert lf.format_size(1024 * 1024) == "1.0 MB"

    def test_gigabytes(self):
        assert lf.format_size(1024**3) == "1.0 GB"

    def test_zero(self):
        assert lf.format_size(0) == "0.0 B"


# ── list_files ─────────────────────────────────────────────────────────────────


class TestListFiles:
    def test_lists_files_in_directory(self, tmp_dir, capsys):
        lf.list_files(str(tmp_dir))
        out = capsys.readouterr().out
        assert "file_a.txt" in out
        assert "file_b.py" in out

    def test_shows_subdirectory(self, tmp_dir, capsys):
        lf.list_files(str(tmp_dir))
        out = capsys.readouterr().out
        assert "subdir" in out

    def test_hides_hidden_files_by_default(self, tmp_dir, capsys):
        hidden = tmp_dir / ".hidden_file"
        hidden.write_text("secret")
        lf.list_files(str(tmp_dir), show_hidden=False)
        out = capsys.readouterr().out
        assert ".hidden_file" not in out

    def test_shows_hidden_files_when_requested(self, tmp_dir, capsys):
        hidden = tmp_dir / ".hidden_file"
        hidden.write_text("secret")
        lf.list_files(str(tmp_dir), show_hidden=True)
        out = capsys.readouterr().out
        assert ".hidden_file" in out

    def test_nonexistent_directory(self, capsys):
        lf.list_files("/nonexistent/path/xyz")
        out = capsys.readouterr().out
        assert "not found" in out.lower() or "❌" in out


# ── find_large_files ───────────────────────────────────────────────────────────


class TestFindLargeFiles:
    def test_finds_largest_file(self, tmp_path, capsys):
        big = tmp_path / "big.dat"
        small = tmp_path / "small.dat"
        big.write_bytes(b"x" * 10_000)
        small.write_bytes(b"x" * 100)
        fl.find_large_files(str(tmp_path), top_n=2)
        out = capsys.readouterr().out
        assert "big.dat" in out

    def test_respects_min_size_filter(self, tmp_path, capsys):
        big = tmp_path / "big.dat"
        small = tmp_path / "small.dat"
        big.write_bytes(b"x" * 10_000)
        small.write_bytes(b"x" * 100)
        # min_size_mb > size of big.dat → nothing should appear
        fl.find_large_files(str(tmp_path), top_n=5, min_size_mb=1.0)
        out = capsys.readouterr().out
        assert "big.dat" not in out

    def test_nonexistent_path(self, capsys):
        fl.find_large_files("/nonexistent/xyz", top_n=5)
        out = capsys.readouterr().out
        assert "not found" in out.lower() or "❌" in out


# ── find_duplicates / hash_file ────────────────────────────────────────────────


class TestHashFile:
    def test_hash_is_consistent(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        h1 = fd.hash_file(f)
        h2 = fd.hash_file(f)
        assert h1 == h2

    def test_different_content_different_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("hello")
        f2.write_text("world")
        assert fd.hash_file(f1) != fd.hash_file(f2)

    def test_same_content_same_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        content = "identical content"
        f1.write_text(content)
        f2.write_text(content)
        assert fd.hash_file(f1) == fd.hash_file(f2)

    def test_hash_is_hex_string(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("data")
        h = fd.hash_file(f)
        assert isinstance(h, str)
        assert len(h) == 64  # SHA-256 hex digest is always 64 chars
        int(h, 16)  # Raises ValueError if not valid hex


class TestFindDuplicates:
    def test_detects_duplicate_files(self, tmp_path):
        content = b"duplicate content " * 100
        (tmp_path / "file1.dat").write_bytes(content)
        (tmp_path / "file2.dat").write_bytes(content)
        (tmp_path / "unique.dat").write_bytes(b"unique " * 100)
        dupes = fd.find_duplicates(str(tmp_path))
        assert len(dupes) == 1
        paths = list(dupes.values())[0]
        assert len(paths) == 2

    def test_no_duplicates_returns_empty(self, tmp_path):
        (tmp_path / "a.txt").write_text("aaa")
        (tmp_path / "b.txt").write_text("bbb")
        dupes = fd.find_duplicates(str(tmp_path))
        assert dupes == {}

    def test_empty_files_not_counted(self, tmp_path):
        (tmp_path / "empty1.txt").write_bytes(b"")
        (tmp_path / "empty2.txt").write_bytes(b"")
        dupes = fd.find_duplicates(str(tmp_path))
        assert dupes == {}


# ── backup ─────────────────────────────────────────────────────────────────────


class TestBackupFile:
    def test_backup_creates_copy(self, tmp_path):
        src = tmp_path / "original.txt"
        src.write_text("important data")
        dest_dir = tmp_path / "backups"
        result = bf.backup_file(str(src), str(dest_dir))
        assert result.exists()
        assert result.read_text() == "important data"

    def test_backup_filename_contains_timestamp(self, tmp_path):
        src = tmp_path / "report.txt"
        src.write_text("data")
        dest_dir = tmp_path / "backups"
        result = bf.backup_file(str(src), str(dest_dir))
        assert "backup" in result.name
        assert result.suffix == ".txt"

    def test_backup_nonexistent_file_raises(self, tmp_path):
        import pytest

        with pytest.raises(FileNotFoundError):
            bf.backup_file(str(tmp_path / "missing.txt"), str(tmp_path))


class TestBackupDirectory:
    def test_backup_copies_tree(self, tmp_path):
        src = tmp_path / "source"
        src.mkdir()
        (src / "a.txt").write_text("file a")
        (src / "b.txt").write_text("file b")
        dest_dir = tmp_path / "backups"
        result = bf.backup_directory(str(src), str(dest_dir))
        assert result.is_dir()
        assert (result / "a.txt").exists()
        assert (result / "b.txt").exists()

    def test_backup_directory_name_includes_original(self, tmp_path):
        src = tmp_path / "myproject"
        src.mkdir()
        (src / "file.txt").write_text("x")
        dest_dir = tmp_path / "backups"
        result = bf.backup_directory(str(src), str(dest_dir))
        assert "myproject" in result.name

    def test_verify_backup_passes_for_good_backup(self, tmp_path):
        src = tmp_path / "source"
        src.mkdir()
        (src / "data.txt").write_text("content" * 100)
        dest_dir = tmp_path / "backups"
        result = bf.backup_directory(str(src), str(dest_dir))
        assert bf.verify_backup(str(src), str(result)) is True
