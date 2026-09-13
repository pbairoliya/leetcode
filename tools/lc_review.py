"""lc_review.py — the nightly reading doc.

One note per day that you read before bed: what you solved today, what spaced
repetition says is due, and the pattern sheet transcluded underneath. Everything
here is *derived* from the problem notes, so the reading doc is disposable —
delete it and `lc review` rebuilds it. Never edit it; edit the problem note.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys

import lc_render
from lccore import (
    LcError,
    compose,
    config,
    dump_frontmatter,  # noqa: F401  (compose uses it; kept for symmetry)
    fmt_duration,
    iter_notes,
    open_in_obsidian,
    write_atomic,
)

READING_DIRNAME = "Reading"
PATTERNS_NOTE = "Leetcode Patterns"
NOTE_TYPE = "leetcode-reading"

BADGE = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}


def _badge(meta) -> str:
    return BADGE.get(str(meta.get("difficulty", "")).lower(), "⚪️")


def _note_link(path) -> str:
    """An Obsidian wikilink to a problem note, by filename."""
    return f"[[{path.stem}]]"


def _is_solved(meta) -> bool:
    return str(meta.get("status", "")).lower() in config().publish_statuses


def _blockquote(text: str) -> str:
    return "\n".join(f"> {line}" if line else ">" for line in text.splitlines())


def _problem_block(path, meta, body) -> str:
    """One problem, written the way you'd want to re-read it: idea, code, traps."""
    head = f"### {meta.get('id')}. {meta.get('title')}"
    facts = [f"{_badge(meta)} {meta.get('difficulty', '?')}"]
    if meta.get("time_spent_min"):
        facts.append(fmt_duration(meta.get("time_spent_min")))
    if int(meta.get("attempts") or 1) > 1:
        facts.append(f"{meta['attempts']} attempts")
    facts.append(_note_link(path))

    parts = [head, " · ".join(facts)]

    approach = lc_render.section(body, lc_render.H_APPROACH)
    if approach and not lc_render.is_placeholder_prose(approach):
        parts.append("**The idea**\n\n" + approach)

    code = lc_render.extract_code(body)
    if code:
        parts.append("**Cover this and say the idea out loud first.**\n\n"
                     f"```python\n{code}\n```")

    complexity = lc_render.section(body, lc_render.H_COMPLEXITY)
    if complexity and "O()" not in complexity:
        parts.append(complexity)

    explanation = lc_render.section(body, lc_render.H_EXPLANATION)
    if explanation and not lc_render.is_placeholder_prose(explanation):
        parts.append("> [!note]- Walk through it\n" + _blockquote(explanation))

    mistakes = lc_render.section(body, lc_render.H_MISTAKES)
    if mistakes and mistakes.strip() not in ("-", ""):
        parts.append("**Remember**\n\n" + mistakes)

    return "\n\n".join(parts)


def _due_block(path, meta, body) -> str:
    mistakes = lc_render.section(body, lc_render.H_MISTAKES)
    line = f"- {_badge(meta)} {_note_link(path)} — last solved {meta.get('date', '?')}"
    if mistakes and mistakes.strip() not in ("-", ""):
        first = next((l for l in mistakes.splitlines() if l.strip()), "")
        line += f"\n  {first.strip()}"
    return line


def build(today: dt.date) -> tuple[dict, str]:
    rows = iter_notes()
    iso = today.isoformat()

    todays = [
        (p, m, b) for p, m, b in rows
        if _is_solved(m) and str(m.get("date")) == iso
    ]
    todays.sort(key=lambda r: int(r[1].get("id") or 0))

    todays_paths = {p for p, _, _ in todays}
    due = [
        (p, m, b) for p, m, b in rows
        if _is_solved(m)
        and p not in todays_paths
        and m.get("next_review")
        and str(m["next_review"]) <= iso
    ]
    due.sort(key=lambda r: str(r[1].get("next_review")))

    minutes = sum(int(m.get("time_spent_min") or 0) for _, m, _ in todays)

    meta = {
        "type": NOTE_TYPE,
        "title": f"Reading — {iso}",
        "date": iso,
        "solved_today": len(todays),
        "due_count": len(due),
        "tags": ["leetcode", "reading"],
    }

    out = [f"# 🌙 Reading — {today:%A, %d %B %Y}"]

    if todays:
        summary = f"**{len(todays)}** solved today"
        if minutes:
            summary += f" · **{fmt_duration(minutes)}** at the keyboard"
        out.append(summary)
    out.append(
        "> [!tip] How to read this\n"
        "> Cover the code. Say the idea out loud. *Then* look. If the words don't\n"
        "> come, that problem isn't learned yet — the code being familiar is not the\n"
        "> same thing."
    )

    out.append("## Today")
    if todays:
        out.extend(_problem_block(p, m, b) for p, m, b in todays)
    else:
        out.append("*Nothing solved today.* Read the patterns below instead — five\nminutes of recall beats zero minutes of new problems.")

    out.append("## Due for review")
    if due:
        out.append("Spaced repetition says these are going stale. Can you still explain them?\n")
        out.extend(_due_block(p, m, b) for p, m, b in due)
    else:
        out.append("Nothing due. 🎉")

    out.append("## Pattern recognition")
    out.append(f"![[{PATTERNS_NOTE}]]")

    return meta, "\n\n".join(out) + "\n"


def reading_path(today: dt.date):
    return config().notes_dir / READING_DIRNAME / f"{today.isoformat()}.md"


def cmd_review(args) -> int:
    today = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    meta, body = build(today)
    text = compose(meta, body)

    if args.print:
        sys.stdout.write(text)
        return 0

    path = reading_path(today)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_atomic(path, text)
    print(f"📖 {path.name} — {meta['solved_today']} solved, {meta['due_count']} due")
    print(f"   {path}")
    if args.open:
        open_in_obsidian(path)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lc review", add_help=True)
    parser.add_argument("review", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("--date", help="build the doc for a past day (YYYY-MM-DD)")
    parser.add_argument("--print", action="store_true", help="write to stdout instead of the vault")
    parser.add_argument("--open", action="store_true", help="open it in Obsidian when done")
    args = parser.parse_args(argv)
    try:
        return cmd_review(args)
    except LcError as exc:
        print(f"lc: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
