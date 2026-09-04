"""lc_stats.py — terminal dashboard, in-flight status, and commit subjects."""
from __future__ import annotations

import argparse
import datetime as dt
import statistics
import sys
from collections import Counter

from lccore import (
    LcError,
    config,
    fmt_duration,
    iter_notes,
    now,
    parse_ts,
)
from lc_sync import _streak, _as_date

BAR = "█"


def _rows():
    return [(p, m, b) for p, m, b in iter_notes()]


def cmd_stats(_args) -> int:
    rows = _rows()
    solved = [m for _, m, _ in rows if str(m.get("status")).lower() in config().publish_statuses]
    if not solved:
        print("Nothing solved yet. Start with:  lc new <url>")
        return 0

    by_diff = Counter(str(m.get("difficulty", "Unknown")).capitalize() for m in solved)
    times = [int(m.get("time_spent_min") or 0) for m in solved if m.get("time_spent_min")]
    dates = [d for d in (_as_date(m.get("date")) for m in solved) if d]
    topics = Counter(t for m in solved for t in (m.get("topics") or []))

    noun = "problem" if len(solved) == 1 else "problems"
    total = f"{sum(times)}m" if not sum(times) else fmt_duration(sum(times))
    print(f"\n  {len(solved)} {noun} solved · {total} total\n")
    widest = max((by_diff.get(d, 0) for d in ("Easy", "Medium", "Hard")), default=1) or 1
    for name, icon in (("Easy", "🟢"), ("Medium", "🟡"), ("Hard", "🔴")):
        n = by_diff.get(name, 0)
        print(f"  {icon} {name:<7} {n:>3}  {BAR * int(24 * n / widest)}")

    print()
    if times:
        print(f"  median solve   {fmt_duration(int(statistics.median(times)))}")
        print(f"  fastest        {fmt_duration(min(times))}")
        print(f"  slowest        {fmt_duration(max(times))}")
    print(f"  streak         {_streak(dates, dt.date.today())} day(s)")
    print(f"  last solved    {max(dates).isoformat() if dates else '—'}")

    if topics:
        print("\n  top topics")
        for name, n in topics.most_common(8):
            print(f"    {name:<28} {n}")

    due = [
        m for _, m, _ in rows
        if m.get("next_review") and str(m["next_review"]) <= dt.date.today().isoformat()
    ]
    if due:
        print(f"\n  ⏰ {len(due)} due for review")
        for m in due[:8]:
            print(f"    {m.get('id'):>4}  {m.get('title')}  (last {m.get('date')})")
    print()
    return 0


def cmd_status(_args) -> int:
    """What's on the bench: unsolved problems, and any running clock."""
    open_rows = [
        (p, m) for p, m, _ in _rows()
        if str(m.get("status", "")).lower() not in config().publish_statuses
    ]
    if not open_rows:
        print("Nothing in flight. All problems are solved.")
        return 0
    print()
    for _, m in open_rows[:12]:
        started = parse_ts(m.get("started_at"))
        banked = int(m.get("time_spent_min") or 0)
        if started:
            live = banked + int((now() - started).total_seconds() // 60)
            mark = f"▶ running {fmt_duration(live)}"
        else:
            mark = f"⏸ {fmt_duration(banked)} banked" if banked else "· not started"
        print(f"  {str(m.get('id') or '?'):>4}  {str(m.get('title'))[:38]:<40} {mark}")
    print()
    return 0


def cmd_commit_subject(_args) -> int:
    """Subject line for the nightly commit, from what was solved today."""
    today = dt.date.today().isoformat()
    fresh = [
        m for _, m, _ in _rows()
        if str(m.get("status")).lower() in config().publish_statuses
        and str(m.get("date")) == today
    ]
    if not fresh:
        print(f"leetcode: sync {today}")
        return 0
    names = ", ".join(f"{m.get('id')} {m.get('title')}" for m in fresh[:3])
    if len(fresh) > 3:
        names += f", +{len(fresh) - 3} more"
    noun = "problem" if len(fresh) == 1 else "problems"
    print(f"leetcode: {len(fresh)} {noun} — {names} ({today})")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="lc stats")
    ap.add_argument("cmd", nargs="?", default="stats", choices=["stats", "status"])
    ap.add_argument("--commit-subject", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.commit_subject:
            return cmd_commit_subject(args)
        return cmd_status(args) if args.cmd == "status" else cmd_stats(args)
    except LcError as exc:
        print(f"lc: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
