"""lc_sync.py — vault notes -> git repo (solution.py + README.md + stats).

Reconciliation rule, in order of precedence:
  1. Note block has real code            -> it wins, written to solution.py
  2. Note block is a stub, file has code -> the file wins, written back to the note
  3. Neither has code                    -> problem skipped, warned about
This is what makes "the note is the source of truth" safe: an untouched
starter block can never erase work done in an editor.
"""
from __future__ import annotations

import argparse
import datetime as dt
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import lc_render
from lccore import (
    GEN_BEGIN,
    GEN_END,
    LcError,
    compose,
    config,
    fmt_duration,
    iter_notes,
    log,
    problem_dir,
    problem_dirname,
    write_atomic,
)

DOCSTRING_QUOTES = ('"""', "'''")


def _strip_header(code: str) -> str:
    """Drop the generated docstring and import preamble before comparing code.

    Must handle a single-line docstring as well as a multi-line one: getting
    this wrong makes a stub file look like real work and defeats the guard in
    reconcile_code.
    """
    text = code.lstrip()
    for quote in DOCSTRING_QUOTES:
        if text.startswith(quote):
            end = text.find(quote, len(quote))
            if end != -1:
                text = text[end + len(quote):]
            break
    lines = text.split("\n")
    while lines and (
        not lines[0].strip()
        or lines[0].startswith(("from typing import", "import typing"))
    ):
        lines.pop(0)
    return "\n".join(lines).strip()


def _file_header(meta: dict[str, Any]) -> str:
    spent = int(meta.get("time_spent_min") or 0)
    solved = f'Solved {meta.get("date")}'
    if spent:
        solved += f" in {fmt_duration(spent)}"
    return (
        f'"""{meta.get("id")}. {meta.get("title")} ({meta.get("difficulty")})\n\n'
        f'{meta.get("link")}\n'
        f'{solved}.\n"""\n'
        "from typing import List, Optional  # noqa: F401\n\n\n"
    )


def reconcile_code(meta: dict[str, Any], body: str, path: Path) -> tuple[str, str, str]:
    """Returns (code, source, new_body). source is 'note' | 'file' | ''."""
    note_code = lc_render.extract_code(body)
    file_code = ""
    if path.exists():
        file_code = _strip_header(path.read_text(encoding="utf-8"))

    if not lc_render.is_placeholder_code(note_code):
        return note_code, "note", body
    if not lc_render.is_placeholder_code(file_code):
        # Pull the editor's version back into the note so the two agree.
        return file_code, "file", lc_render.replace_code(body, file_code)
    return "", "", body


# --------------------------------------------------------------------------- readmes


def render_problem_readme(meta: dict[str, Any], body: str) -> str:
    topics = ", ".join(f"`{t}`" for t in meta.get("topics") or []) or "—"
    rows = [
        f"# {meta.get('id')}. {meta.get('title')}",
        "",
        f"[Problem on LeetCode]({meta.get('link')})",
        "",
        "| | |",
        "|---|---|",
        f"| **Difficulty** | {lc_render.difficulty_badge(str(meta.get('difficulty')))} |",
        f"| **Topics** | {topics} |",
        f"| **Time to solve** | {fmt_duration(meta.get('time_spent_min'))} |",
        f"| **Attempts** | {meta.get('attempts', 1)} |",
        f"| **Solved** | {meta.get('date', '—')} |",
    ]
    if meta.get("solved_without_help") is not None:
        rows.append(f"| **Unaided** | {'yes' if meta['solved_without_help'] else 'no'} |")
    rows.append("")

    for heading in lc_render.PUBLISHED_SECTIONS:
        text = lc_render.section(body, heading)
        if lc_render.is_placeholder_prose(text):
            continue
        rows += [f"## {heading}", "", text, ""]

    rows += ["## Solution", "", "See [`solution.py`](./solution.py).", ""]
    return "\n".join(rows).rstrip() + "\n"


def _streak(dates: list[dt.date], today: dt.date) -> int:
    """Consecutive days ending today or yesterday that have a solve."""
    days = set(dates)
    if not days:
        return 0
    cursor = today if today in days else today - dt.timedelta(days=1)
    if cursor not in days:
        return 0
    count = 0
    while cursor in days:
        count += 1
        cursor -= dt.timedelta(days=1)
    return count


def render_root_readme(entries: list[dict[str, Any]], existing: str = "") -> str:
    today = dt.date.today()
    by_diff = Counter(e["difficulty"] for e in entries)
    topics = Counter(t for e in entries for t in e["topics"])
    times = [e["minutes"] for e in entries if e["minutes"]]
    dates = [e["date"] for e in entries if e["date"]]

    block = [GEN_BEGIN, "", "## Stats", ""]
    block += [
        "| Metric | Value |",
        "|---|---|",
        f"| **Solved** | {len(entries)} |",
        f"| 🟢 Easy | {by_diff.get('Easy', 0)} |",
        f"| 🟡 Medium | {by_diff.get('Medium', 0)} |",
        f"| 🔴 Hard | {by_diff.get('Hard', 0)} |",
        f"| **Median solve time** | {fmt_duration(int(statistics.median(times))) if times else '—'} |",
        f"| **Total time** | {fmt_duration(sum(times))} |",
        f"| **Current streak** | {_streak(dates, today)} day(s) |",
        f"| **Last solved** | {max(dates).isoformat() if dates else '—'} |",
        "",
    ]

    if topics:
        block += ["## Topics", ""]
        block += [" ".join(f"`{name} ×{n}`" for name, n in topics.most_common(24)), ""]

    block += ["## Problems", "", "| # | Problem | Difficulty | Time | Attempts | Solved |", "|---|---|---|---|---|---|"]
    for e in sorted(entries, key=lambda x: (x["date"] or dt.date.min), reverse=True):
        link = f"[{e['title']}](./{e['difficulty']}/{e['dirname']})"
        block.append(
            f"| {e['id']} | {link} | {lc_render.difficulty_badge(e['difficulty'])} "
            f"| {fmt_duration(e['minutes'])} | {e['attempts']} | {e['date'] or '—'} |"
        )
    block += ["", f"_Updated {today.isoformat()} by `lc sync`._", "", GEN_END]
    generated = "\n".join(block)

    # Preserve anything the user wrote outside the markers.
    if existing and GEN_BEGIN in existing and GEN_END in existing:
        head = existing.split(GEN_BEGIN)[0]
        tail = existing.split(GEN_END, 1)[1]
        return head + generated + tail
    intro = "# LeetCode\n\nSolutions and write-ups, generated from my Obsidian vault by [`lc`](./tools).\n\n"
    return intro + generated + "\n"


# --------------------------------------------------------------------------- sync


def sync(dry_run: bool = False, verbose: bool = True) -> dict[str, Any]:
    cfg = config()
    entries: list[dict[str, Any]] = []
    skipped: list[str] = []
    written: list[Path] = []

    for note_path, meta, body in iter_notes():
        status = str(meta.get("status") or "").lower()
        if status not in cfg.publish_statuses:
            continue

        directory = problem_dir(meta)
        code_path = directory / "solution.py"
        code, source, new_body = reconcile_code(meta, body, code_path)

        if not code:
            skipped.append(f"{meta.get('title')}: no solution in the note or in {code_path.name}")
            continue

        readme = render_problem_readme(meta, new_body)
        file_text = _file_header(meta) + code.strip() + "\n"

        if dry_run:
            for p, text in ((code_path, file_text), (directory / "README.md", readme)):
                if not p.exists() or p.read_text(encoding="utf-8") != text:
                    written.append(p)
        else:
            if write_atomic(code_path, file_text):
                written.append(code_path)
            if write_atomic(directory / "README.md", readme):
                written.append(directory / "README.md")
            if source == "file" and new_body != body:
                write_atomic(note_path, compose(meta, new_body))
                if verbose:
                    log(f"  ← pulled code from {code_path.name} into the note")

        entries.append({
            "id": str(meta.get("id") or "").lstrip("0") or "0",
            "title": meta.get("title"),
            "difficulty": str(meta.get("difficulty") or "Unknown").capitalize(),
            "dirname": problem_dirname(meta),
            "topics": list(meta.get("topics") or []),
            "minutes": int(meta.get("time_spent_min") or 0),
            "attempts": int(meta.get("attempts") or 1),
            "date": _as_date(meta.get("date")),
            "source": source,
        })

    root = cfg.repo_dir / "README.md"
    existing = root.read_text(encoding="utf-8") if root.exists() else ""
    readme = render_root_readme(entries, existing)
    if dry_run:
        if readme != existing:
            written.append(root)
    elif write_atomic(root, readme):
        written.append(root)

    return {"entries": entries, "skipped": skipped, "written": written}


def _as_date(value: Any) -> dt.date | None:
    try:
        return dt.date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="lc sync")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    try:
        result = sync(dry_run=args.dry_run, verbose=not args.quiet)
    except LcError as exc:
        print(f"lc: {exc}", file=sys.stderr)
        return 1

    prefix = "would write" if args.dry_run else "wrote"
    if not args.quiet:
        for p in result["written"]:
            try:
                rel = p.relative_to(config().repo_dir)
            except ValueError:
                rel = p
            print(f"  {prefix} {rel}")
    for s in result["skipped"]:
        print(f"  ⚠ skipped {s}", file=sys.stderr)
    print(f"{len(result['entries'])} problem(s) published, {len(result['written'])} file(s) {prefix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
