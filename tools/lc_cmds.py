"""lc_cmds.py — the note-facing subcommands: new, start, pause, resume, done, refresh.

Invoked by the `lc` bash dispatcher as `python3 lc_cmds.py <subcommand> ...`.
Every command prints one human line to stdout and exits non-zero on failure.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import Any

import lc_fetch
import lc_render
from lccore import (
    GEN_BEGIN,
    NOTE_TYPE,
    GEN_END,
    LcError,
    compose,
    config,
    find_note,
    fmt_duration,
    iter_notes,
    log,
    now,
    obsidian_uri,
    open_in_obsidian,
    parse_ts,
    problem_dir,
    sanitize_filename,
    split_frontmatter,
    write_atomic,
)

STATUS_OPEN = ("attempted", "in-progress", "paused")


def _note_path_for(title: str, pid: Any) -> Path:
    """`0001 Two Sum.md` — the id prefix keeps the folder sorted like LeetCode."""
    pid = str(pid or "").zfill(4)
    return config().notes_dir / f"{pid} {sanitize_filename(title)}.md"


def _save(path: Path, meta: dict[str, Any], body: str) -> bool:
    return write_atomic(path, compose(meta, body))


# --------------------------------------------------------------------------- new


def cmd_new(args) -> int:
    try:
        problem = lc_fetch.get_problem(args.target, refresh=args.refresh)
    except LcError as exc:
        if args.offline or "network" in str(exc):
            log(f"! {exc}\n! falling back to an offline stub note")
            problem = lc_fetch.stub_problem(args.target)
        else:
            raise

    path = _note_path_for(problem["title"], problem["id"])

    if path.exists():
        # Re-opening a problem you have seen before: bump attempts, restart the
        # clock, and keep every word you already wrote.
        meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
        meta["attempts"] = int(meta.get("attempts") or 1) + 1
        meta["status"] = "attempted"
        meta["started_at"] = now().isoformat()
        meta["ended_at"] = None
        _save(path, meta, body)
        if args.print:
            print(compose(meta, body))
        else:
            print(f"↻ attempt #{meta['attempts']} on {problem['title']} — clock restarted")
            open_in_obsidian(path)
        return 0

    meta, body = lc_render.render_note(problem)
    meta["started_at"] = now().isoformat()
    meta["status"] = "attempted"

    if args.print:
        # Templater path: emit the note and let Obsidian create the file.
        print(compose(meta, body))
        _scaffold_code(meta, problem["starter"])
        return 0

    _save(path, meta, body)
    code_path = _scaffold_code(meta, problem["starter"])
    print(f"✓ {problem['id']}. {problem['title']} ({problem['difficulty']})")
    print(f"  note  {path}")
    print(f"  code  {code_path}")
    print(f"  clock started at {now():%H:%M}")
    if not args.no_open:
        open_in_obsidian(path)
    return 0


def _scaffold_code(meta: dict[str, Any], starter: str) -> Path:
    """Write solution.py with LeetCode's stub, but never clobber real work."""
    directory = problem_dir(meta)
    path = directory / "solution.py"
    header = (
        f'"""{meta["id"]}. {meta["title"]} ({meta["difficulty"]})\n\n'
        f'{meta["link"]}\n"""\n'
        "from typing import List, Optional  # noqa: F401\n\n\n"
    )
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if not lc_render.is_placeholder_code(existing, starter):
            return path
    write_atomic(path, header + starter.rstrip() + "\n")
    return path


# --------------------------------------------------------------------------- timer


def _elapsed_min(meta: dict[str, Any], end: dt.datetime) -> int:
    started = parse_ts(meta.get("started_at"))
    if not started:
        return int(meta.get("time_spent_min") or 0)
    delta = max(0, int((end - started).total_seconds() // 60))
    return int(meta.get("time_spent_min") or 0) + delta


def cmd_start(args) -> int:
    path, meta, body = find_note(args.target)
    meta["started_at"] = now().isoformat()
    meta["ended_at"] = None
    if meta.get("status") not in STATUS_OPEN:
        meta["status"] = "attempted"
        meta["attempts"] = int(meta.get("attempts") or 1) + 1
    _save(path, meta, body)
    banked = int(meta.get("time_spent_min") or 0)
    extra = f" (resuming, {fmt_duration(banked)} banked)" if banked else ""
    print(f"▶ {meta.get('title')} — clock started at {now():%H:%M}{extra}")
    return 0


def cmd_pause(args) -> int:
    path, meta, body = find_note(args.target)
    if not parse_ts(meta.get("started_at")):
        raise LcError(f"{meta.get('title')} has no running clock")
    meta["time_spent_min"] = _elapsed_min(meta, now())
    meta["started_at"] = None
    meta["status"] = "paused"
    _save(path, meta, body)
    print(f"⏸ {meta.get('title')} — {fmt_duration(meta['time_spent_min'])} banked")
    return 0


def cmd_resume(args) -> int:
    return cmd_start(args)


def _next_review(meta: dict[str, Any], today: dt.date) -> str:
    ladder = config().review_ladder.get(
        str(meta.get("difficulty", "medium")).lower(), [2, 7, 21, 60]
    )
    solves = max(0, int(meta.get("solves") or 0))
    days = ladder[min(solves, len(ladder) - 1)]
    return (today + dt.timedelta(days=days)).isoformat()


def cmd_done(args) -> int:
    path, meta, body = find_note(args.target)
    end = now()
    meta["time_spent_min"] = _elapsed_min(meta, end)
    meta["ended_at"] = end.isoformat()
    meta["started_at"] = meta.get("started_at") or None
    meta["status"] = "solved"
    meta["solves"] = int(meta.get("solves") or 0) + 1
    if args.unaided is not None:
        meta["solved_without_help"] = args.unaided
    meta["next_review"] = _next_review(meta, dt.date.today())
    if not meta.get("date"):
        meta["date"] = dt.date.today().isoformat()

    body = _refresh_stats(meta, body)
    _save(path, meta, body)

    spent = meta["time_spent_min"]
    took = f"in {fmt_duration(spent)}" if spent else "(no time recorded)"
    print(f"✓ solved {meta.get('title')} {took}")
    warnings = _completeness_warnings(meta, body)
    for w in warnings:
        print(f"  ⚠ {w}")
    print(f"  next review {meta['next_review']}")
    return 0


def _completeness_warnings(meta: dict[str, Any], body: str) -> list[str]:
    """Tell the user now what `lc sync` would otherwise silently skip tonight."""
    out = []
    code = lc_render.extract_code(body)
    if lc_render.is_placeholder_code(code):
        out.append("no solution in the note's python block — sync will use solution.py if it has one")
    if lc_render.is_placeholder_prose(lc_render.section(body, lc_render.H_EXPLANATION)):
        out.append("Explanation is empty — the repo README will be thin")
    if "O()" in lc_render.section(body, lc_render.H_COMPLEXITY):
        out.append("Complexity is still O()")
    return out


def _refresh_stats(meta: dict[str, Any], body: str) -> str:
    """Keep a one-line stats strip directly under the title, inside the markers."""
    import re

    line = f"> {lc_render.stats_line(meta)}"
    existing = re.compile(r"^> \*\*Status:\*\*.*$", re.M)
    if existing.search(body):
        return existing.sub(lambda _: line, body, count=1)
    # Insert just above the first "## " heading, which is always ## Problem.
    m = re.search(r"^##\s+", body, re.M)
    if not m:
        return body.rstrip() + f"\n\n{line}\n"
    return body[: m.start()].rstrip() + f"\n\n{line}\n\n" + body[m.start():]


# --------------------------------------------------------------------------- refresh


def cmd_refresh(args) -> int:
    """Re-pull the problem statement, keeping everything the user wrote.

    Only the block between the lc markers is replaced.
    """
    targets = [find_note(args.target)] if args.target else iter_notes()
    changed = 0
    for path, meta, body in targets:
        if not meta.get("slug"):
            continue
        try:
            problem = lc_fetch.get_problem(str(meta["slug"]), refresh=True)
        except LcError as exc:
            log(f"! {path.name}: {exc}")
            continue
        fresh = lc_render.render_body(problem)
        new_head = fresh.split(GEN_END)[0]
        if GEN_BEGIN in body and GEN_END in body:
            body = new_head + GEN_END + body.split(GEN_END, 1)[1]
        else:
            body = new_head + GEN_END + "\n\n" + body
        meta["difficulty"] = problem["difficulty"]
        meta["topics"] = problem["topics"]
        meta["id"] = problem["id"]
        meta["link"] = problem["link"]
        body = _refresh_stats(meta, body)
        if _save(path, meta, body):
            changed += 1
            print(f"↻ {path.name}")
    print(f"refreshed {changed} note(s)")
    return 0


# --------------------------------------------------------------------------- migrate


OLD_SECTION_MAP = {
    "Initial plan": lc_render.H_APPROACH,
    "Key insight": lc_render.H_EXPLANATION,
    "Mistakes / what to remember next time": lc_render.H_MISTAKES,
}
TEMPLATER_LEFTOVER = re.compile(r"<%.*?%>", re.S)


def _old_subsection(body: str, heading: str) -> str:
    """Read a '### heading' block out of the pre-lc template's Notes section."""
    m = re.search(rf"^###[ \t]+{re.escape(heading)}[ \t]*$", body, re.M)
    if not m:
        return ""
    rest = body[m.end():]
    nxt = re.search(r"^#{2,3}[ \t]+", rest, re.M)
    text = (rest[: nxt.start()] if nxt else rest)
    return TEMPLATER_LEFTOVER.sub("", text).strip()


def cmd_migrate(args) -> int:
    """Rebuild pre-lc notes in the current format, keeping everything written.

    Idempotent: notes that already carry `type: leetcode` are left alone, so
    this is safe to re-run.
    """
    folder = config().notes_dir
    converted = 0
    for path in sorted(folder.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        meta, body = split_frontmatter(text)
        if meta.get("type") == NOTE_TYPE:
            continue
        if not meta.get("link") and not meta.get("title"):
            continue  # a freeform journal note, not a problem note

        target = str(meta.get("link") or meta.get("title") or path.stem)
        try:
            problem = lc_fetch.get_problem(target)
        except LcError as exc:
            log(f"! {path.name}: {exc}")
            continue

        new_meta, new_body = lc_render.render_note(problem)
        # Carry over everything the user actually wrote.
        code = lc_render.extract_code(body)
        if not lc_render.is_placeholder_code(code):
            new_body = lc_render.replace_code(new_body, code)
        complexity = lc_render.section(body, "Complexity")
        if complexity and "O()" not in complexity:
            new_body = lc_render.replace_section(new_body, lc_render.H_COMPLEXITY, complexity)
        for old_head, new_head in OLD_SECTION_MAP.items():
            carried = _old_subsection(body, old_head)
            if carried and not lc_render.is_placeholder_prose(carried):
                new_body = lc_render.replace_section(new_body, new_head, carried)

        new_meta["date"] = meta.get("date") or new_meta["date"]
        new_meta["attempts"] = int(meta.get("attempts") or 1)
        old_time = meta.get("time_spent") or meta.get("time_spent_min")
        new_meta["time_spent_min"] = int(old_time) if str(old_time).isdigit() else 0
        if not lc_render.is_placeholder_code(code):
            new_meta["status"] = "solved"
            new_meta["solves"] = 1
            new_meta["ended_at"] = None
            new_meta["next_review"] = _next_review(new_meta, dt.date.today())
        new_body = _refresh_stats(new_meta, new_body)

        dest = _note_path_for(new_meta["title"], new_meta["id"])
        _save(dest, new_meta, new_body)
        if dest != path:
            if args.keep:
                log(f"  kept the original at {path.name}")
            else:
                path.unlink()
        print(f"↻ {path.name} -> {dest.name}")
        converted += 1

    print(f"migrated {converted} note(s)")
    if converted:
        print("run `lc sync` to publish them")
    return 0


# --------------------------------------------------------------------------- misc


def cmd_open(args) -> int:
    path, meta, _ = find_note(args.target)
    print(obsidian_uri(path))
    open_in_obsidian(path)
    return 0


def cmd_alias(args) -> int:
    lc_fetch.problem_index()
    problem = lc_fetch.get_problem(args.leetcode)
    lc_fetch.save_alias(args.foreign.strip().lower(), problem["slug"])
    print(f"✓ {args.foreign} -> {problem['slug']} ({problem['title']})")
    return 0


def cmd_path(args) -> int:
    """Used by the Templater 'done' template to find the note for a file."""
    path, meta, _ = find_note(args.target)
    print(path)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lc", add_help=True)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("new")
    p.add_argument("target")
    p.add_argument("--print", action="store_true", help="emit the note to stdout instead of writing it")
    p.add_argument("--no-open", action="store_true")
    p.add_argument("--refresh", action="store_true", help="bypass the problem cache")
    p.add_argument("--offline", action="store_true")
    p.set_defaults(func=cmd_new)

    for name, fn in (("start", cmd_start), ("pause", cmd_pause), ("resume", cmd_resume)):
        p = sub.add_parser(name)
        p.add_argument("target", nargs="?")
        p.set_defaults(func=fn)

    p = sub.add_parser("done")
    p.add_argument("target", nargs="?")
    p.add_argument("--unaided", dest="unaided", action="store_true", default=None)
    p.add_argument("--helped", dest="unaided", action="store_false")
    p.set_defaults(func=cmd_done)

    p = sub.add_parser("refresh")
    p.add_argument("target", nargs="?")
    p.set_defaults(func=cmd_refresh)

    p = sub.add_parser("migrate")
    p.add_argument("--keep", action="store_true", help="leave the original file in place")
    p.set_defaults(func=cmd_migrate)

    p = sub.add_parser("open")
    p.add_argument("target", nargs="?")
    p.set_defaults(func=cmd_open)

    p = sub.add_parser("path")
    p.add_argument("target", nargs="?")
    p.set_defaults(func=cmd_path)

    p = sub.add_parser("alias")
    p.add_argument("foreign")
    p.add_argument("leetcode")
    p.set_defaults(func=cmd_alias)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except LcError as exc:
        print(f"lc: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
