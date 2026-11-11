#!/usr/bin/env python3
"""Per-book counts of duplicate problems and of pagination padding.

All parts of a multipart book are taken together. For each book print
the number of active problems, the number of problems commented out as
duplicates, and how many more problems the book needs to end on a full
page (12 problems) or a full two-page spread (24 problems).
"""

from validate import discover_groups, parse_references

PROBLEMS_PER_PAGE = 12
PROBLEMS_PER_SPREAD = 24


def padding(count, unit):
    return -count % unit


def main():
    rows = []
    for base, files in discover_groups().items():
        active = 0
        duplicates = set()
        for tex in files:
            refs, commented = parse_references(tex)
            active += len(refs)
            duplicates.update(
                (level, pid)
                for level, pid, _, _, tag in commented
                if tag.startswith("duplicate")
            )
        rows.append((base, active, len(duplicates)))

    width = max(len(base) for base, _, _ in rows)
    print(
        f"{'book':<{width}}  {'problems':>8}  {'duplicates':>10}"
        f"  {'to 12':>5}  {'to 24':>5}"
    )
    for base, active, duplicates in rows:
        print(
            f"{base:<{width}}  {active:>8}  {duplicates:>10}"
            f"  {padding(active, PROBLEMS_PER_PAGE):>5}"
            f"  {padding(active, PROBLEMS_PER_SPREAD):>5}"
        )


if __name__ == "__main__":
    main()
