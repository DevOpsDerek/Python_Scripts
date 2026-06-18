"""
Exercise 08 — Environment Inspector  ✅ SOLUTION
"""

import os


def get_env_vars(prefix: str = "", search: str = "") -> list:
    items = list(os.environ.items())
    if prefix:
        items = [(n, v) for n, v in items if n.lower().startswith(prefix.lower())]
    if search:
        sl = search.lower()
        items = [(n, v) for n, v in items if sl in n.lower() or sl in v.lower()]
    return sorted(items, key=lambda x: x[0].lower())


def truncate(value: str, max_len: int) -> str:
    return value if len(value) <= max_len else value[: max_len - 1] + "…"


def print_report(variables: list, total: int, show_full: bool) -> None:
    if not variables:
        print("  No matching environment variables found.\n")
        return

    col_width = max((len(n) for n, _ in variables), default=15)
    col_width = max(col_width, 15)

    print()
    for name, value in variables:
        display_value = value if show_full else truncate(value, 80)
        print(f"  {name:<{col_width}}  {display_value}")

    print(f"\n  {len(variables)} variable(s) shown (of {total} total).\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", default="")
    parser.add_argument("--search", default="")
    parser.add_argument("--values", action="store_true")
    args = parser.parse_args()

    total = len(os.environ)
    title_parts = []
    if args.prefix:
        title_parts.append(f"prefix: '{args.prefix}'")
    if args.search:
        title_parts.append(f"search: '{args.search}'")
    filter_desc = f"  (filter: {', '.join(title_parts)})" if title_parts else ""

    print(f"\n  Environment Variables{filter_desc}")
    print("  " + "─" * 55)

    results = get_env_vars(args.prefix, args.search)
    print_report(results, total, args.values)
