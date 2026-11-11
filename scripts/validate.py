#!/usr/bin/env python3
r"""Check that each book references every problem available for it.

A book's problems live in problems/<base>/<level>/<id>.sgf and are
referenced from books/<base>.tex (or books/<base>-part-N.tex) as
\p{<level>}{<id>}. A multipart book is validated as the union of all of
its parts against the whole problems/<base> directory.

Missing problems are classified using duplicates.log: a problem that
also exists in another book is reported separately from a problem that
is not referenced anywhere else. Exit status is non-zero when a unique
problem is missing, a reference has no problem file, a render file is
not a gnos diagram, or (with --strict) a problem is only present in a
commented-out line. Use --ignore-duplicates to also accept missing
problems duplicated in other books.

Each missing problem is printed as the TeX line that would add it, in
the comment style the books use for layout: a problem listed in
high-problems.log is suggested as %full-goban, one listed in
wide-problems.log as %halfgoban, and one duplicated in another book as
%duplicate. A problem in no log is suggested active.
"""

import argparse
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books"
PROBLEMS = ROOT / "problems"

PART_RE = re.compile(r"^(?P<base>.+)-part-(?P<num>\d+)$")
REF_RE = re.compile(r"\\p\{([^{}]+)\}\{([^{}]+)\}")
# Generated render files are a gnos diagram, optionally preceded by the
# eliminated note the extractor writes on the first line of a solution.
GNOS_HEADER_RE = re.compile(r"(?:\\solutionnote\{[^{}]*\}%\s*)?\{\\gnos\b")


def split_comment(line):
    """Split a TeX line into (code, comment), respecting escaped \\%."""
    for i, char in enumerate(line):
        if char != "%":
            continue
        backslashes = 0
        j = i - 1
        while j >= 0 and line[j] == "\\":
            backslashes += 1
            j -= 1
        if backslashes % 2 == 0:
            return line[:i], line[i + 1:]
    return line, ""


def clean_tag(text):
    return text.strip().strip("%").strip()


def parse_references(path):
    active = []
    commented = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for lineno, line in enumerate(text.splitlines(), 1):
        code, comment = split_comment(line)
        for match in REF_RE.finditer(code):
            active.append((match.group(1), match.group(2), path, lineno, clean_tag(comment)))
        for match in REF_RE.finditer(comment):
            commented.append(
                (match.group(1), match.group(2), path, lineno, clean_tag(comment[match.end():]))
            )
    return active, commented


def part_number(path):
    match = PART_RE.match(path.stem)
    return int(match.group("num")) if match else 0


def discover_groups():
    groups = defaultdict(list)
    for tex in sorted(BOOKS.glob("*.tex")):
        if tex.name == "header.tex":
            continue
        match = PART_RE.match(tex.stem)
        groups[match.group("base") if match else tex.stem].append(tex)
    for files in groups.values():
        files.sort(key=part_number)
    return dict(groups)


def load_expected(base):
    root = PROBLEMS / base
    if not root.is_dir():
        return None
    root = root.resolve()
    expected = {}
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if not name.endswith(".sgf"):
                continue
            path = Path(dirpath) / name
            rel = path.relative_to(root)
            if len(rel.parts) != 2:
                print(f"warning: unexpected path problems/{base}/{rel}", file=sys.stderr)
                continue
            expected[(rel.parts[0], path.stem)] = path
    return expected


def problem_dir(base, key):
    if PROBLEMS.joinpath(base).exists():
        return (PROBLEMS / base / key[0]).resolve()
    return PROBLEMS / base / key[0]


def check_problem_files(base, key):
    directory = problem_dir(base, key)
    missing = []
    for ext in (".gnos", ".solution"):
        if not directory.joinpath(key[1] + ext).is_file():
            missing.append(ext)
    return missing


def check_problem_format(base, key):
    """Render files whose content is not a gnos diagram.

    The book inputs these files directly, so a plain-text or truncated
    file still compiles and prints its raw content instead of a board.
    """
    directory = problem_dir(base, key)
    malformed = []
    for ext in (".gnos", ".solution"):
        path = directory.joinpath(key[1] + ext)
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not GNOS_HEADER_RE.match(text.lstrip()):
            malformed.append(ext)
    return malformed


def describe(key):
    return f"\\p{{{key[0]}}}{{{key[1]}}}"


def location(entry):
    path, lineno, tag = entry
    suffix = f"  [{tag}]" if tag else ""
    return f"{path.relative_to(ROOT)}:{lineno}{suffix}"


def load_log_paths(path):
    """Set of problem paths listed in a classification log.

    high-problems.log and wide-problems.log hold one path per line;
    duplicates.log prefixes each path with a digest, so the last field
    is the path either way.
    """
    if not path or not path.is_file():
        return set()
    paths = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if parts:
            paths.add(parts[-1])
    return paths


def layout_tag(base, key, high_paths, wide_paths):
    """Comment tag a book uses for a problem that is not rendered.

    A problem too tall for the truncated diagram needs the whole goban;
    one that is only too wide still fits the half goban.  A tall
    problem is also wide, so the tall classification wins.
    """
    rel = f"problems/{base}/{key[0]}/{key[1]}.sgf"
    if rel in high_paths:
        return "full-goban"
    if rel in wide_paths:
        return "halfgoban"
    return None


def suggest(key, tag):
    """The TeX line that adds a problem to a book, commented if tagged."""
    ref = describe(key)
    return f"%{ref}%{tag}" if tag else f"{ref}%"


def load_duplicates(path):
    """Map each problem path to the other paths with identical content."""
    groups = defaultdict(list)
    group_of = {}
    if path and path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            parts = line.split(None, 1)
            if len(parts) == 2:
                digest, rel = parts
                groups[digest].append(rel)
                group_of[rel] = digest

    def elsewhere(rel):
        digest = group_of.get(rel)
        if digest is None:
            return []
        return [other for other in groups[digest] if other != rel]

    return elsewhere


def validate(
    base,
    files,
    duplicates_elsewhere,
    high_paths,
    wide_paths,
    strict,
    verbose,
    ignore_duplicates,
    separator=False,
):
    expected = load_expected(base)
    if expected is None:
        if separator:
            print()
        print(f"{base}: MISSING problems/{base} directory")
        return False, True

    active = defaultdict(list)
    commented = defaultdict(list)
    for tex in files:
        refs, disabled = parse_references(tex)
        for level, pid, path, lineno, tag in refs:
            active[(level, pid)].append((path, lineno, tag))
        for level, pid, path, lineno, tag in disabled:
            commented[(level, pid)].append((path, lineno, tag))

    expected_keys = set(expected)
    active_keys = set(active)
    commented_keys = set(commented)

    missing = sorted(expected_keys - active_keys - commented_keys)
    only_commented = sorted((expected_keys & commented_keys) - active_keys)
    extra = sorted(active_keys - expected_keys)
    extra_commented = sorted(commented_keys - expected_keys)
    duplicates = {key: refs for key, refs in active.items() if len(refs) > 1}
    broken = {key: check_problem_files(base, key) for key in active_keys & expected_keys}
    broken = {key: exts for key, exts in broken.items() if exts}
    malformed = {}
    for key in active_keys & expected_keys:
        if key in broken:
            continue
        exts = check_problem_format(base, key)
        if exts:
            malformed[key] = exts

    missing_unique = []
    missing_elsewhere = []
    for key in missing:
        others = duplicates_elsewhere(f"problems/{base}/{key[0]}/{key[1]}.gnos")
        if others:
            missing_elsewhere.append((key, others))
        else:
            missing_unique.append(key)

    ok = True
    if missing_unique:
        ok = False
    if missing_elsewhere and not ignore_duplicates:
        ok = False
    if extra or broken or malformed:
        ok = False
    if strict and only_commented:
        ok = False

    has_output = (
        missing_unique
        or missing_elsewhere
        or extra
        or broken
        or malformed
        or extra_commented
        or duplicates
        or (only_commented and (verbose or strict))
    )
    if not has_output:
        return ok, False

    if separator:
        print()
    label = ", ".join(tex.name for tex in files)
    print(f"== {base} ({label})")
    print(
        f"   on disk: {len(expected_keys)}"
        f" | active: {len(active_keys)}"
        f" | commented out: {len(only_commented)}"
        f" | missing: {len(missing)}"
        f" ({len(missing_unique)} unique, {len(missing_elsewhere)} duplicate elsewhere)"
    )

    if missing_unique:
        tagged = [(key, layout_tag(base, key, high_paths, wide_paths)) for key in missing_unique]
        counts = Counter(tag or "active" for _, tag in tagged)
        detail = ", ".join(
            f"{counts[name]} {name}"
            for name in ("halfgoban", "full-goban", "active")
            if counts[name]
        )
        print(f"   MISSING (no reference at all): {len(missing_unique)} unique ({detail})")
        for key, tag in tagged:
            print(f"     {suggest(key, tag)}")
    if missing_elsewhere:
        if verbose:
            print(f"   MISSING, DUPLICATED IN OTHER BOOKS: {len(missing_elsewhere)}")
            for key, others in missing_elsewhere:
                print(f"     {suggest(key, 'duplicate')}  also {', '.join(others)}")
        else:
            note = "ignored" if ignore_duplicates else "use -v to list"
            print(f"   MISSING, DUPLICATED IN OTHER BOOKS: {len(missing_elsewhere)} ({note})")
    if extra:
        print(f"   EXTRA (no problem file): {len(extra)}")
        for key in extra:
            print(f"     {describe(key)}  " + ", ".join(location(e) for e in active[key]))
    if broken:
        print(f"   BROKEN (missing render files): {len(broken)}")
        for key, exts in sorted(broken.items()):
            print(f"     {describe(key)}  missing {' '.join(exts)}  " + ", ".join(location(e) for e in active[key]))
    if malformed:
        print(f"   MALFORMED (not a gnos diagram): {len(malformed)}")
        for key, exts in sorted(malformed.items()):
            print(f"     {describe(key)}  bad {' '.join(exts)}  " + ", ".join(location(e) for e in active[key]))
    if extra_commented:
        print(f"   COMMENTED BUT NO PROBLEM FILE: {len(extra_commented)}")
        for key in extra_commented:
            print(f"     {describe(key)}  " + ", ".join(location(e) for e in commented[key]))
    if duplicates:
        print(f"   DUPLICATE references: {len(duplicates)}")
        for key in sorted(duplicates):
            print(f"     {describe(key)}  " + ", ".join(location(e) for e in duplicates[key]))
    if only_commented and verbose:
        print(f"   COMMENTED OUT (present but disabled): {len(only_commented)}")
        for key in only_commented:
            print(f"     {describe(key)}  " + ", ".join(location(e) for e in commented[key]))
    if strict and only_commented and not verbose:
        print(f"   --strict: {len(only_commented)} commented-out problem(s) count as missing")
    return ok, True


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("books", nargs="*", help="book name, part name, or path (e.g. books/foo.tex)")
    parser.add_argument("--all", action="store_true", help="validate every book")
    parser.add_argument("--strict", action="store_true", help="treat commented-out problems as missing")
    parser.add_argument(
        "--ignore-duplicates",
        action="store_true",
        help="do not fail for missing problems that also exist in another book",
    )
    parser.add_argument(
        "--duplicates-log",
        default=str(ROOT / "duplicates.log"),
        help="duplicate report used to classify missing problems (default: duplicates.log)",
    )
    parser.add_argument(
        "--high-problems-log",
        default=str(ROOT / "high-problems.log"),
        help="problems needing the full goban (default: high-problems.log)",
    )
    parser.add_argument(
        "--wide-problems-log",
        default=str(ROOT / "wide-problems.log"),
        help="problems needing the half goban (default: wide-problems.log)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="list commented-out and duplicate-missing problems")
    args = parser.parse_args()

    duplicates_elsewhere = load_duplicates(Path(args.duplicates_log))
    high_paths = load_log_paths(Path(args.high_problems_log))
    wide_paths = load_log_paths(Path(args.wide_problems_log))
    groups = discover_groups()
    if args.all:
        targets = [(base, groups[base]) for base in sorted(groups)]
    else:
        if not args.books:
            parser.error("give one or more books, or use --all")
        targets = []
        for raw in args.books:
            name = Path(raw).name
            if name.endswith(".tex"):
                name = name[:-4]
            match = PART_RE.match(name)
            if match and match.group("base") in groups:
                targets.append((match.group("base"), groups[match.group("base")]))
            elif name in groups:
                targets.append((name, groups[name]))
            else:
                parser.error(f"no such book: {raw}")

    failures = 0
    reported = False
    for base, files in targets:
        ok, has_output = validate(
            base,
            files,
            duplicates_elsewhere,
            high_paths,
            wide_paths,
            args.strict,
            args.verbose,
            args.ignore_duplicates,
            separator=reported,
        )
        reported = reported or has_output
        if not ok:
            failures += 1

    print()
    print(f"{len(targets)} book(s) checked, {failures} with problems")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
