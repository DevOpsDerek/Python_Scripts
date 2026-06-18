"""
conftest.py — Shared pytest fixtures and module loader for the SysAdmin Script Library.

Because the scripts aren't a Python package (no __init__.py in each folder),
we use importlib.util to load them by file path. The load_script() helper
in this file makes that easy for every test module.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

# Root of the project — two levels up from this conftest.py
PROJECT_ROOT = Path(__file__).parent.parent


def load_script(relative_path: str):
    """Load a project script as a module by its relative path.

    Usage:
        mod = load_script("01_filesystem/list_files.py")
        mod.format_size(1024)

    Args:
        relative_path: Path relative to the project root.

    Returns:
        The loaded module object.
    """
    full_path = PROJECT_ROOT / relative_path
    module_name = relative_path.replace("/", "_").replace(".py", "")

    # Return cached module if already loaded
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, full_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


# ── Shared fixtures ────────────────────────────────────────────────────────────


@pytest.fixture()
def tmp_dir(tmp_path):
    """A temporary directory pre-populated with a small file tree."""
    (tmp_path / "subdir").mkdir()
    (tmp_path / "file_a.txt").write_text("hello world\n" * 100)
    (tmp_path / "file_b.py").write_text("print('hi')\n" * 50)
    (tmp_path / "file_c.log").write_text("ERROR something went wrong\nINFO all good\n")
    (tmp_path / "subdir" / "nested.txt").write_text("nested content\n" * 20)
    (tmp_path / "subdir" / "image.png").write_bytes(b"\x89PNG" + b"\x00" * 100)
    return tmp_path


@pytest.fixture()
def sample_log(tmp_path):
    """A temporary log file with a mix of log levels."""
    content = "\n".join(
        [
            "Jun 18 10:00:01 host app[123]: INFO Server started",
            "Jun 18 10:00:02 host app[123]: INFO Listening on port 8080",
            "Jun 18 10:00:05 host app[123]: WARNING High memory usage: 85%",
            "Jun 18 10:00:10 host app[123]: ERROR Failed to connect to database",
            "Jun 18 10:00:11 host app[123]: ERROR Retrying connection (attempt 1/3)",
            "Jun 18 10:00:15 host app[123]: CRITICAL Database connection pool exhausted",
            "Jun 18 10:00:20 host app[123]: INFO Connection restored",
            "Jun 18 10:00:25 host app[123]: DEBUG Cache miss for key: user_42",
        ]
    )
    log_file = tmp_path / "test.log"
    log_file.write_text(content)
    return log_file
