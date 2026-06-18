#!/usr/bin/env python3
"""
lint.py — Run ruff linting across the entire SysAdmin Script Library
=====================================================================
Usage:
    python lint.py              # Check all scripts, report issues
    python lint.py --fix        # Auto-fix safe issues
    python lint.py --file path  # Lint a single file
    python lint.py --explain    # Explain the rules being enforced

This script wraps `ruff` and adds:
  - A beginner-friendly summary of what each rule category means
  - Coloured pass/fail output per file
  - A final score (% of files that are clean)
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------
def green(s: str) -> str:
    return f"\033[92m{s}\033[0m"


def red(s: str) -> str:
    return f"\033[91m{s}\033[0m"


def yellow(s: str) -> str:
    return f"\033[93m{s}\033[0m"


def bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


# ---------------------------------------------------------------------------
# Human-readable descriptions for the rule codes beginners will encounter
# ---------------------------------------------------------------------------
RULE_EXPLANATIONS = {
    "E": "PEP 8 style issues (spacing, indentation, blank lines)",
    "W": "PEP 8 warnings (trailing whitespace, deprecated syntax)",
    "F": "Pyflakes: unused imports, undefined names, shadowed variables",
    "I": "isort: imports should be sorted and grouped correctly",
    "UP": "pyupgrade: use modern Python syntax (e.g. f-strings, |type| unions)",
    "B": "flake8-bugbear: common bugs, mutable defaults, broad exceptions",
    "SIM": "flake8-simplify: suggests simpler, more Pythonic code patterns",
}


def check_ruff_installed() -> bool:
    """Return True if ruff is available on PATH."""
    result = subprocess.run(
        ["ruff", "--version"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def run_ruff(targets: list[str], fix: bool = False) -> dict:
    """Run ruff and return parsed JSON output.

    Args:
        targets: List of file/directory paths to check.
        fix:     If True, apply safe auto-fixes.

    Returns:
        Dict with keys 'diagnostics' (list) and 'returncode' (int).
    """
    cmd = ["ruff", "check", "--output-format=json"]
    if fix:
        cmd.append("--fix")
    cmd.extend(targets)

    result = subprocess.run(cmd, capture_output=True, text=True)

    diagnostics = []
    if result.stdout.strip():
        try:
            diagnostics = json.loads(result.stdout)
        except json.JSONDecodeError:
            pass

    return {
        "diagnostics": diagnostics,
        "returncode": result.returncode,
        "stderr": result.stderr,
    }


def group_by_file(diagnostics: list) -> dict:
    """Group diagnostics by filename.

    Returns:
        Dict mapping filename → list of diagnostic dicts.
    """
    grouped: dict = {}
    for d in diagnostics:
        fname = d.get("filename", "unknown")
        grouped.setdefault(fname, []).append(d)
    return grouped


def print_explain() -> None:
    """Print a guide to the lint rule categories."""
    print(f"\n  {bold('LINT RULE GUIDE')}\n")
    print("  The following rule sets are active in this project:\n")
    for prefix, desc in RULE_EXPLANATIONS.items():
        print(f"  {bold(prefix):<15} {desc}")
    print()
    print("  To look up any specific rule, run:")
    print(dim("    ruff rule <code>   e.g.  ruff rule F401"))
    print()


def print_report(result: dict, fix: bool) -> int:
    """Print a human-readable lint report.

    Args:
        result: Output from run_ruff().
        fix:    Whether --fix mode was used.

    Returns:
        Exit code: 0 = all clean, 1 = issues found.
    """
    diagnostics = result["diagnostics"]
    by_file = group_by_file(diagnostics)

    # Collect all Python files in the project for the per-file pass/fail list
    root = Path(__file__).parent
    all_py_files = sorted(root.rglob("*.py"))
    # Exclude lint.py itself from the "scored" files
    all_py_files = [f for f in all_py_files if f.name != "lint.py"]

    clean_count = 0
    dirty_count = 0

    print(f"\n  {bold('LINT RESULTS')}\n")

    for py_file in all_py_files:
        rel = py_file.relative_to(root)
        file_issues = by_file.get(str(py_file), [])

        if not file_issues:
            print(f"  {green('✓')} {rel}")
            clean_count += 1
        else:
            print(f"  {red('✗')} {rel}  {yellow(f'({len(file_issues)} issue(s))')}")
            dirty_count += 1

            for issue in file_issues:
                row = issue.get("location", {}).get("row", "?")
                col = issue.get("location", {}).get("column", "?")
                code = issue.get("code", "?")
                msg = issue.get("message", "")
                fixable = " [auto-fixable]" if issue.get("fix") else ""
                print(f"       {dim(f'line {row}:{col}')}  {yellow(code)}  {msg}{dim(fixable)}")

    # Summary
    total = clean_count + dirty_count
    score = int(clean_count / total * 100) if total else 100

    print()
    print("  " + "─" * 55)

    if dirty_count == 0:
        print(f"  {green('✅ All ' + str(total) + ' files are clean!')}  Score: {green('100%')}")
    else:
        colour = green if score >= 80 else (yellow if score >= 50 else red)
        print(f"  {red(f'{dirty_count} file(s) have issues')}  |  {colour(f'{score}% clean')}")
        if not fix:
            print(f"\n  {dim('Tip: Run  python lint.py --fix  to auto-fix safe issues.')}")

    print()
    return 0 if dirty_count == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lint all Python scripts in the SysAdmin Script Library.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python lint.py                  check everything
  python lint.py --fix            auto-fix safe issues
  python lint.py --file 01_filesystem/list_files.py
  python lint.py --explain        show what the rules mean
        """,
    )
    parser.add_argument("--fix", action="store_true", help="Auto-fix safe issues in place")
    parser.add_argument("--file", metavar="PATH", help="Lint a single file instead of all scripts")
    parser.add_argument(
        "--explain", action="store_true", help="Print an explanation of the rule categories"
    )
    args = parser.parse_args()

    if args.explain:
        print_explain()
        sys.exit(0)

    if not check_ruff_installed():
        print(red("\n  ❌ ruff is not installed."))
        print("  Install it with:  brew install ruff")
        print("  or:               pip install ruff\n")
        sys.exit(1)

    targets = [args.file] if args.file else ["."]

    if args.fix:
        print(f"\n  {bold('Running ruff with --fix…')}")
    else:
        print(f"\n  {bold('Running ruff…')}")

    result = run_ruff(targets, fix=args.fix)
    exit_code = print_report(result, fix=args.fix)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
