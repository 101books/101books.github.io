#!/usr/bin/env python3
"""Re-split a multi-part collection into evenly sized parts.

A collection is a set of books/<collection>-part-<n>.tex files whose
\\problems block is a sequence of \\p{book}{problem} lines (12 per page).
The tool keeps the problem sequence untouched and only moves the part
boundaries, so every part contains a whole number of 12-problem pages.
Parts are sized in multiples of 24 problems (two pages), as evenly as
possible. The final part takes the leftover, so a collection whose total is
not a multiple of 24 still splits; only that last part may end mid-page.

    ./rebalance.py the-great-tesuji-encyclopedia
    ./rebalance.py the-great-tesuji-encyclopedia --write
"""

import argparse
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

PROBLEMS_PER_PAGE = 12
PROBLEMS_PER_CHUNK = 24  # parts are multiples of this; the last one takes the rest
SOLUTIONS_PER_PAGE = 100

PROBLEMS_BLOCK = re.compile(r"(\\def\\problems\{%\n)(.*?)(\n\}\n)", re.DOTALL)
ACTIVE_PROBLEM = re.compile(r"^\\p\{(\d+)\}\{(\d+)\}")
PART_SUFFIX = re.compile(r"-part-(\d+)\.tex$")


@dataclass
class Part:
    path: Path
    text: str
    match: re.Match
    lines: list[str]
    count: int = field(init=False)

    def __post_init__(self) -> None:
        self.count = count_problems(self.lines)


def find_parts(collection: str) -> list[Path]:
    parts = [
        path
        for path in Path("books").glob(f"{collection}-part-*.tex")
        if PART_SUFFIX.search(path.name)
    ]
    if len(parts) < 2:
        raise SystemExit(
            f"error: expected at least two books/{collection}-part-*.tex files, found {len(parts)}"
        )
    return sorted(parts, key=lambda path: int(PART_SUFFIX.search(path.name).group(1)))


def read_block(path: Path) -> Part:
    text = path.read_text(encoding="utf-8")
    match = PROBLEMS_BLOCK.search(text)
    if match is None:
        raise SystemExit(f"error: no \\def\\problems block in {path}")
    return Part(path, text, match, match.group(2).split("\n"))


def count_problems(lines: list[str]) -> int:
    return sum(1 for line in lines if ACTIVE_PROBLEM.match(line))


def page_count(problems: int) -> int:
    # matches books/header.tex: title page + 12 problems/page + 100 solutions/page
    if problems == 0:
        return 2
    return (
        1
        + math.ceil(problems / PROBLEMS_PER_PAGE)
        + math.ceil(problems / SOLUTIONS_PER_PAGE)
    )


def split_lines(lines: list[str], targets: list[int]) -> list[list[str]]:
    ends = []
    index = 0
    seen = 0
    wanted = 0
    for target in targets:
        wanted += target
        while seen < wanted:
            if ACTIVE_PROBLEM.match(lines[index]):
                seen += 1
            index += 1
        ends.append(index)

    chunks = []
    start = 0
    for end in ends:
        chunks.append(lines[start:end])
        start = end
    chunks[-1].extend(lines[start:])
    return chunks


def part_targets(total: int, count: int) -> list[int]:
    """Problem counts for `count` parts.

    Every part but the last gets a whole number of PROBLEMS_PER_CHUNK chunks,
    spread as evenly as possible; the last part takes whatever is left over, so
    a collection that is not a multiple of PROBLEMS_PER_CHUNK still splits. If
    the leftover would make the last part bigger than the others, chunks move
    forward so the last part stays the smallest.
    """
    chunks_of, remainder = divmod(total, PROBLEMS_PER_CHUNK)
    if chunks_of < count:
        raise SystemExit(
            f"error: {total} problems ({chunks_of} chunks of {PROBLEMS_PER_CHUNK})"
            f" is too few for {count} parts"
        )
    per_part, extra = divmod(chunks_of, count)
    sizes = [
        (per_part + (1 if index < extra else 0)) * PROBLEMS_PER_CHUNK
        for index in range(count)
    ]
    sizes[-1] += remainder
    while count > 1 and sizes[-1] > max(sizes[:-1]):
        smallest = min(range(count - 1), key=sizes.__getitem__)
        sizes[smallest] += PROBLEMS_PER_CHUNK
        sizes[-1] -= PROBLEMS_PER_CHUNK
    return sizes


def missing_render_files(part: Path, chunk: list[str]) -> list[str]:
    missing = []
    for line in chunk:
        match = ACTIVE_PROBLEM.match(line)
        if match:
            book, problem = match.groups()
            path = Path("problems", part.stem, book, f"{problem}.gnos")
            if not path.exists():
                missing.append(str(path))
    return missing


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-split a multi-part collection into evenly sized parts."
    )
    parser.add_argument("collection", help="e.g. the-great-tesuji-encyclopedia")
    parser.add_argument(
        "--write", action="store_true", help="rewrite the .tex files (default: dry run)"
    )
    args = parser.parse_args()

    parts = [read_block(path) for path in find_parts(args.collection)]
    all_lines = [line for part in parts for line in part.lines]
    total = sum(part.count for part in parts)

    if total == 0:
        raise SystemExit(f"error: {args.collection} has no active problems")

    targets = part_targets(total, len(parts))
    chunks = split_lines(all_lines, targets)
    new_counts = [count_problems(chunk) for chunk in chunks]

    old_pages = [page_count(part.count) for part in parts]
    new_pages = [page_count(count) for count in new_counts]

    print(f"{args.collection}: {len(parts)} parts, {total} problems")
    for part, new, old_page, new_page in zip(parts, new_counts, old_pages, new_pages):
        print(
            f"  {part.path.stem:<55} {part.count:>4} problems, {old_page:>3} pages"
            f" -> {new:>4} problems, {new_page:>3} pages"
        )
    print(
        f"  {'total':<55} {total:>4} problems, {sum(old_pages):>3} pages"
        f" -> {sum(new_pages):>3} pages"
    )
    for part, count in zip(parts, new_counts):
        if count == 0:
            print(f"warning: {part.path.stem} gets no problems")

    if not args.write:
        print("dry run: pass --write to update the .tex files")
        return

    missing = [
        path
        for part, chunk in zip(parts, chunks)
        for path in missing_render_files(part.path, chunk)
    ]
    if missing:
        raise SystemExit(
            "error: missing generated problems, not writing anything:\n  "
            + "\n  ".join(missing)
        )

    for part, chunk in zip(parts, chunks):
        text = (
            part.text[: part.match.start(2)]
            + "\n".join(chunk)
            + part.text[part.match.end(2) :]
        )
        if text == part.text:
            print(f"unchanged {part.path}")
            continue
        part.path.write_text(text, encoding="utf-8")
        print(f"updated {part.path}")


if __name__ == "__main__":
    main()
