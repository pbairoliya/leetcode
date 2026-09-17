"""lc_session.py — a guided study session in the terminal.

Builds a block plan out of what the vault actually knows: what you never solved
unaided, what spaced repetition says is due, and what the roadmap says is next.
Interactive by default (Enter reveals an answer, Enter advances a block); with
`--print` it just dumps the plan.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import sys
from pathlib import Path
from typing import Any

from lccore import LcError, config, iter_notes

TOOLS = Path(__file__).resolve().parent

# Share of the session each block gets. Scaled to --minutes, then rounded.
WEIGHTS = {"quiz": 0.10, "redo": 0.17, "review": 0.17, "new": 0.50, "close": 0.06}


# --------------------------------------------------------------------------- data


def _load(name: str) -> Any:
    return json.loads((TOOLS / name).read_text(encoding="utf-8"))


def _solved() -> dict[int, dict]:
    """Problem id -> frontmatter, for everything published as solved."""
    out = {}
    for _, meta, _ in iter_notes():
        pid = str(meta.get("id") or "")
        if pid.isdigit() and str(meta.get("status", "")).lower() in config().publish_statuses:
            out[int(pid)] = meta
    return out


def _needs_redo(solved: dict[int, dict]) -> list[dict]:
    """Problems you got to the answer on, but not on your own."""
    rows = [m for m in solved.values() if m.get("solved_without_help") is False]
    rows.sort(key=lambda m: str(m.get("date")), reverse=True)
    return rows


def _due(solved: dict[int, dict], today: dt.date) -> list[dict]:
    rows = [
        m for m in solved.values()
        if m.get("next_review") and str(m["next_review"]) <= today.isoformat()
    ]
    rows.sort(key=lambda m: str(m.get("next_review")))
    return rows


def _next_up(solved: dict[int, dict], roadmap: dict) -> list[tuple[str, list]]:
    """Unsolved roadmap problems, focus topics first, in the roadmap's own order."""
    out = []
    focus = roadmap["focus"]
    for key in focus + [t for t in roadmap["order"] if t not in focus]:
        topic = roadmap["topics"].get(key)
        if not topic:
            continue
        todo = [p for p in topic["problems"] if p[0] not in solved]
        if todo:
            out.append((topic["name"], todo))
    return out


def _progress(solved: dict[int, dict], roadmap: dict) -> list[tuple[str, int, int]]:
    rows = []
    for key in roadmap["order"]:
        topic = roadmap["topics"][key]
        total = len(topic["problems"])
        if not total:
            continue
        done = sum(1 for p in topic["problems"] if p[0] in solved)
        rows.append((topic["name"], done, total))
    return rows


# --------------------------------------------------------------------------- output


class Out:
    """Printing plus the pauses that make it a session rather than a wall of text."""

    def __init__(self, interactive: bool):
        self.interactive = interactive
        self.color = interactive and sys.stdout.isatty()

    def _c(self, code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.color else text

    def bold(self, text): return self._c("1", text)
    def dim(self, text): return self._c("2", text)
    def cyan(self, text): return self._c("36", text)
    def green(self, text): return self._c("32", text)
    def yellow(self, text): return self._c("33", text)

    def rule(self, char="─", width=72):
        print(self.dim(char * width))

    def block(self, n: int, title: str, minutes: int):
        print()
        self.rule("━")
        print(f" {self.bold(f'{n}. {title}')}  {self.dim(f'~{minutes} min')}")
        self.rule("━")

    def pause(self, prompt: str = "press Enter to continue") -> None:
        if not self.interactive:
            return
        try:
            input(self.dim(f"    ({prompt}) "))
        except (EOFError, KeyboardInterrupt):
            print()
            raise SystemExit(0)


# --------------------------------------------------------------------------- blocks


def block_quiz(out: Out, minutes: int, bank: list[dict], topics: list[str], count: int) -> None:
    out.block(1, "Recall quiz — no notes", minutes)
    print("  Say the answer out loud before revealing. A hesitation is a gap.\n")

    pool = [q for q in bank if q["topic"] in topics] or bank
    picks = random.sample(pool, min(count, len(pool)))
    for i, q in enumerate(picks, 1):
        print(f"  {out.cyan(f'Q{i}')} {out.dim('[' + q['topic'] + ']')}")
        print(f"     {q['q']}")
        if out.interactive:
            out.pause("Enter to reveal")
            print(f"     {out.green('→')} {q['a']}\n")
        else:
            print(f"     {out.dim('→ ' + q['a'])}\n")


def block_redo(out: Out, minutes: int, rows: list[dict]) -> None:
    out.block(2, "Redo from a blank file", minutes)
    if not rows:
        print("  Nothing outstanding — everything solved was solved unaided. 🎉")
        return
    print("  You reached these answers with help. Recognition is not production.")
    print("  Open a blank file. Write the invariant sentence FIRST, then the code.\n")
    for m in rows[:3]:
        print(f"  {out.yellow('▸')} {m.get('id')}. {out.bold(str(m.get('title')))}"
              f"  {out.dim('(last ' + str(m.get('date')) + ')')}")
    if len(rows) > 3:
        print(out.dim(f"    …and {len(rows) - 3} more waiting"))
    print()
    out.pause("done? Enter")


def block_review(out: Out, minutes: int, rows: list[dict]) -> None:
    out.block(3, "Reviews due — explain, don't rewrite", minutes)
    if not rows:
        print("  Nothing due. 🎉")
        return
    print("  Cover the code. Say the idea out loud. If the words don't come,")
    print("  that problem isn't learned yet — the code being familiar isn't the same thing.\n")
    for m in rows[:6]:
        overdue = ""
        try:
            days = (dt.date.today() - dt.date.fromisoformat(str(m["next_review"]))).days
            if days > 0:
                overdue = out.dim(f"  ({days}d overdue)")
        except ValueError:
            pass
        print(f"  {out.yellow('▸')} {m.get('id')}. {out.bold(str(m.get('title')))}{overdue}")
    if len(rows) > 6:
        print(out.dim(f"    …and {len(rows) - 6} more due"))
    print()
    out.pause("done? Enter")


def block_new(out: Out, minutes: int, queue: list[tuple[str, list]], count: int) -> None:
    out.block(4, "New problems", minutes)
    if not queue:
        print("  Roadmap is clear. Add the next topic to tools/roadmap.json.")
        return
    topic, todo = queue[0]
    print(f"  Topic: {out.bold(topic)}   {out.dim('(finish this before opening a new one)')}\n")
    for pid, title, diff, why in todo[:count]:
        print(f"  {out.yellow('▸')} {out.bold(f'{pid}. {title}')}  {out.dim(diff)}")
        print(f"      {why}")
        print(out.dim(f"      lc new {pid}"))
    print()
    print("  Before coding each one, out loud:")
    print("   1. What shape is the answer?")
    print("   2. What does the brute force re-compute?  (the waste names the tool)")
    print("   3. The invariant, as one sentence.")
    print(out.dim("   Stuck 15 min → hint 1 only. 20 min → write the brute force. 25 min → read it,\n"
                  "   then close it and rewrite from blank, and mark the note `lc done --helped`."))
    print()
    out.pause("done? Enter")


def block_close(out: Out, minutes: int, roadmap_rows: list[tuple[str, int, int]]) -> None:
    out.block(5, "Close out", minutes)
    print("  1. Fill in each note: My approach, Explanation, Mistakes.")
    print("  2. Add ONE row to the §8 log in the study guide, and a card if you met")
    print("     something new. A card earns its place only if its 'Tell' is something")
    print("     you could spot in a problem you haven't seen.")
    print("  3. If a problem beat you, write the sentence you wish you'd had at minute two.")
    print(out.dim("     lc review --open     build tonight's reading doc"))
    print(out.dim("     lc push              sync + commit + push"))
    print()
    print(f"  {out.bold('Roadmap')}")
    for name, done, total in roadmap_rows:
        bar_len = 18
        filled = round(bar_len * done / total)
        bar = "█" * filled + "░" * (bar_len - filled)
        mark = out.green("✓") if done == total else " "
        print(f"   {mark} {name:<26} {bar} {done}/{total}")


# --------------------------------------------------------------------------- driver


def cmd_session(args) -> int:
    bank = _load("quiz.json")
    roadmap = _load("roadmap.json")
    solved = _solved()
    today = dt.date.today()

    total = max(20, min(240, args.minutes))
    mins = {k: max(2, round(total * w)) for k, w in WEIGHTS.items()}

    interactive = not args.print and sys.stdin.isatty()
    out = Out(interactive)

    topics = args.topics.split(",") if args.topics else roadmap["focus"] + ["recognition", "complexity"]
    redo = _needs_redo(solved)
    due = _due(solved, today)
    queue = _next_up(solved, roadmap)

    print()
    print(out.bold(f"  LeetCode session — {today:%A %d %B %Y} · {total} min"))
    print(out.dim(f"  {len(solved)} solved · {len(redo)} to redo · {len(due)} due · "
                  f"{sum(len(t) for _, t in queue)} left on the roadmap"))

    block_quiz(out, mins["quiz"], bank, topics, args.questions)
    block_redo(out, mins["redo"], redo)
    block_review(out, mins["review"], due)
    block_new(out, mins["new"], queue, args.problems)
    block_close(out, mins["close"], _progress(solved, roadmap))
    print()
    return 0


def cmd_quiz(args) -> int:
    bank = _load("quiz.json")
    roadmap = _load("roadmap.json")
    out = Out(not args.print and sys.stdin.isatty())
    topics = args.topics.split(",") if args.topics else None
    pool = [q for q in bank if not topics or q["topic"] in topics]
    if not pool:
        raise LcError(f"no questions for {args.topics!r} — "
                      f"topics are: {', '.join(sorted({q['topic'] for q in bank}))}")
    print()
    for i, q in enumerate(random.sample(pool, min(args.questions, len(pool))), 1):
        print(f"  {out.cyan(f'Q{i}')} {out.dim('[' + q['topic'] + ']')}")
        print(f"     {q['q']}")
        if out.interactive:
            out.pause("Enter to reveal")
            print(f"     {out.green('→')} {q['a']}\n")
        else:
            print(f"     {out.dim('→ ' + q['a'])}\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lc session", add_help=True)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("session")
    p.add_argument("--minutes", type=int, default=90, help="total session length (default 90)")
    p.add_argument("--questions", type=int, default=5, help="quiz questions (default 5)")
    p.add_argument("--problems", type=int, default=3, help="new problems to queue (default 3)")
    p.add_argument("--topics", help="comma-separated quiz topics")
    p.add_argument("--print", action="store_true", help="dump the plan, no prompts")
    p.set_defaults(func=cmd_session)

    p = sub.add_parser("quiz")
    p.add_argument("--questions", type=int, default=8)
    p.add_argument("--topics", help="comma-separated topics")
    p.add_argument("--print", action="store_true")
    p.set_defaults(func=cmd_quiz)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except LcError as exc:
        print(f"lc: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
