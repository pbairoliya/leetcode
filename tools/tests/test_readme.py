"""Repo README generation: stats, streaks, and preserving hand-written text."""
import datetime as dt

import lc_sync
from lccore import GEN_BEGIN, GEN_END


def entry(**kw):
    base = dict(id="1", title="Two Sum", difficulty="Easy", dirname="0001-two-sum",
                topics=["Array"], minutes=30, attempts=1, date=dt.date(2026, 9, 3),
                source="note")
    return {**base, **kw}


def test_streak_counts_back_from_today():
    today = dt.date(2026, 9, 3)
    days = [today, today - dt.timedelta(days=1), today - dt.timedelta(days=2)]
    assert lc_sync._streak(days, today) == 3


def test_streak_tolerates_not_having_solved_yet_today():
    today = dt.date(2026, 9, 3)
    assert lc_sync._streak([today - dt.timedelta(days=1)], today) == 1


def test_streak_breaks_on_a_gap():
    today = dt.date(2026, 9, 3)
    assert lc_sync._streak([today, today - dt.timedelta(days=4)], today) == 1
    assert lc_sync._streak([], today) == 0
    assert lc_sync._streak([today - dt.timedelta(days=3)], today) == 0


def test_root_readme_has_the_headline_numbers():
    md = lc_sync.render_root_readme([
        entry(), entry(id="2", title="Add Two Numbers", difficulty="Medium",
              dirname="0002-add-two-numbers", minutes=50),
    ])
    assert "| **Solved** | 2 |" in md
    assert "| 🟢 Easy | 1 |" in md
    assert "| 🟡 Medium | 1 |" in md
    assert "[Two Sum](./Easy/0001-two-sum)" in md
    assert "40m" in md, "median of 30 and 50"


def test_handwritten_text_outside_the_markers_survives():
    existing = f"# My repo\n\nA personal note.\n\n{GEN_BEGIN}\nold\n{GEN_END}\n\n## Licence\n\nMIT\n"
    md = lc_sync.render_root_readme([entry()], existing)
    assert "A personal note." in md
    assert "## Licence" in md
    assert "old" not in md


def test_regenerating_is_stable():
    once = lc_sync.render_root_readme([entry()])
    assert lc_sync.render_root_readme([entry()], once) == once


def test_problem_readme_omits_untouched_sections():
    meta = dict(id="1", title="Two Sum", difficulty="Easy", link="https://x",
                topics=["Array"], time_spent_min=30, attempts=1, date="2026-09-03")
    body = ("## My approach\n\nUse a dict.\n\n"
            "## Complexity\n\n**Time:** `O(n)`\n\n"
            "## Explanation\n\n- \n\n"
            "## Mistakes / what to remember\n\n- \n")
    md = lc_sync.render_problem_readme(meta, body)
    assert "Use a dict." in md
    assert "## Explanation" not in md, "empty bullet is not real content"
    assert "## Mistakes" not in md
    assert "solution.py" in md
