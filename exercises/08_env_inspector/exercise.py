"""
Exercise 08 — Environment Inspector
======================================
GOAL: Write a script that displays environment variables in a readable
table, with options to filter by prefix and search by keyword.

Expected output example:
    Environment Variables  (filter: 'PATH')
    ─────────────────────────────────────────────────
    PATH           /usr/local/bin:/usr/bin:/bin:/usr/sbin
    PYTHONPATH     /home/user/lib

    2 variable(s) shown (of 58 total).

CONCEPTS YOU WILL PRACTISE:
  - os.environ             — accessing environment variables
  - dict methods           — .items(), .keys()
  - String methods         — .startswith(), .lower(), 'in' operator
  - Sorting                — sorted() with a key function
  - argparse               — multiple optional arguments

HOW TO RUN:
    python exercise.py                    (show all variables)
    python exercise.py --prefix PATH      (variables starting with PATH)
    python exercise.py --search python    (variables containing 'python')
    python exercise.py --prefix HOME --values  (show full values)
"""

import os


def get_env_vars(prefix: str = "", search: str = "") -> list:
    """Return a filtered, sorted list of (name, value) environment variable pairs.

    Filtering rules:
      - If `prefix` is given: only include variables whose name starts with
        the prefix (case-insensitive).
      - If `search` is given: only include variables whose name OR value
        contains the search string (case-insensitive).
      - If both are given, BOTH conditions must match.

    Args:
        prefix: Filter by variable name prefix (e.g. 'PYTHON').
        search: Search string to find in name or value.

    Returns:
        Sorted list of (name, value) tuples.

    Hint: os.environ.items() yields (name, value) pairs.
    """
    # TODO: Start with all variables from os.environ.items().
    # TODO: Apply the prefix filter if prefix is non-empty.
    # TODO: Apply the search filter if search is non-empty.
    # TODO: Sort by variable name (alphabetical, case-insensitive).
    # TODO: Return the filtered list.
    pass


def truncate(value: str, max_len: int) -> str:
    """Truncate a string to max_len characters, adding '…' if cut off.

    Args:
        value:   String to truncate.
        max_len: Maximum allowed length including the ellipsis.

    Returns:
        The original string if it fits, otherwise a truncated version ending in '…'.
    """
    # TODO: Return value if len(value) <= max_len.
    # TODO: Otherwise return value[:max_len - 1] + '…'
    pass


def print_report(variables: list, total: int, show_full: bool) -> None:
    """Print the environment variable table.

    Args:
        variables:  List of (name, value) tuples to display.
        total:      Total number of env vars (before filtering).
        show_full:  If True, show full values; if False, truncate long values.
    """
    if not variables:
        print("  No matching environment variables found.\n")
        return

    # Find the longest variable name for column alignment
    max_name_len = max(len(name) for name, _ in variables)
    col_width = max(max_name_len, 15)  # Minimum 15 chars wide

    print()
    for name, value in variables:
        display_value = value if show_full else truncate(value, 80)
        # TODO: Print each variable — name left-aligned to col_width, then value.
        # Hint: f"  {name:<{col_width}}  {display_value}"
        pass

    print(f"\n  {len(variables)} variable(s) shown (of {total} total).\n")


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Inspect environment variables.")
    parser.add_argument("--prefix", default="", help="Filter by name prefix (e.g. PYTHON)")
    parser.add_argument("--search", default="", help="Search in name or value")
    parser.add_argument("--values", action="store_true", help="Show full values (no truncation)")
    args = parser.parse_args()

    total_vars = len(os.environ)
    title_parts = []
    if args.prefix:
        title_parts.append(f"prefix: '{args.prefix}'")
    if args.search:
        title_parts.append(f"search: '{args.search}'")
    filter_desc = f"  (filter: {', '.join(title_parts)})" if title_parts else ""

    print(f"\n  Environment Variables{filter_desc}")
    print("  " + "─" * 55)

    # TODO: Call get_env_vars() with the filter arguments.
    # TODO: Call print_report() with the results.
    pass


# ── HINTS ─────────────────────────────────────────────────────────────────────
# 1. os.environ is a dict-like object: os.environ['HOME'] gives your home dir.
# 2. os.environ.items() yields ('NAME', 'value') tuples.
# 3. 'substring'.lower() in 'STRING'.lower() does a case-insensitive 'contains' check.
# 4. sorted(list, key=lambda x: x[0].lower()) sorts by the first element, ignoring case.
