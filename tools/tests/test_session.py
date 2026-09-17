"""The study-session planner: who needs a redo, what's due, what's next."""
import datetime as dt
import json
from pathlib import Path

import lc_session
import pytest

TOOLS = Path(lc_session.__file__).resolve().parent
TODAY = dt.date(2026, 9, 16)


@pytest.fixture(scope="module")
def roadmap():
    return json.loads((TOOLS / "roadmap.json").read_text())


@pytest.fixture(scope="module")
def bank():
    return json.loads((TOOLS / "quiz.json").read_text())


# ------------------------------------------------------------------ data files


def test_roadmap_topics_cover_the_declared_order(roadmap):
    assert set(roadmap["order"]) == set(roadmap["topics"])
    assert set(roadmap["focus"]) <= set(roadmap["order"])


def test_roadmap_problem_rows_are_well_formed(roadmap):
    seen = {}
    for key, topic in roadmap["topics"].items():
        for row in topic["problems"]:
            pid, title, diff, why = row              # exactly four fields
            assert isinstance(pid, int) and pid > 0
            assert diff in ("Easy", "Medium", "Hard"), (key, title)
            assert why.strip(), (key, title)
            assert pid not in seen, f"{pid} listed in {seen.get(pid)} and {key}"
            seen[pid] = key


def test_quiz_entries_are_well_formed(bank, roadmap):
    extra = {"recognition", "complexity", "hashing"}
    allowed = set(roadmap["order"]) | extra
    for q in bank:
        assert q["topic"] in allowed, q["topic"]
        # a prompt, not a fragment — a question or an imperative ("justify …")
        assert q["q"].strip()[-1] in "?.", q["q"]
        assert len(q["a"]) > 20, q["q"]


# ------------------------------------------------------------------ selection


def meta(pid, **kw):
    return {"id": str(pid), "title": f"P{pid}", "date": "2026-09-01", **kw}


def test_redo_lists_only_the_problems_you_needed_help_on():
    solved = {
        1: meta(1, solved_without_help=True),
        2: meta(2, solved_without_help=False),
        3: meta(3, solved_without_help=None),
    }
    assert [m["id"] for m in lc_session._needs_redo(solved)] == ["2"]


def test_redo_puts_the_most_recent_failure_first():
    solved = {
        1: meta(1, solved_without_help=False, date="2026-09-01"),
        2: meta(2, solved_without_help=False, date="2026-09-15"),
    }
    assert [m["id"] for m in lc_session._needs_redo(solved)] == ["2", "1"]


def test_due_includes_today_and_everything_overdue():
    solved = {
        1: meta(1, next_review="2026-09-15"),
        2: meta(2, next_review="2026-09-16"),
        3: meta(3, next_review="2026-09-17"),
        4: meta(4),
    }
    assert [m["id"] for m in lc_session._due(solved, TODAY)] == ["1", "2"]


def test_due_is_ordered_most_overdue_first():
    solved = {
        1: meta(1, next_review="2026-09-16"),
        2: meta(2, next_review="2026-09-10"),
    }
    assert [m["id"] for m in lc_session._due(solved, TODAY)] == ["2", "1"]


def test_next_up_skips_solved_and_keeps_roadmap_order(roadmap):
    solved = {p[0]: meta(p[0]) for p in roadmap["topics"]["arrays"]["problems"][:2]}
    queue = lc_session._next_up(solved, roadmap)
    name, todo = queue[0]
    assert name == "Arrays & Hashing"
    assert [p[0] for p in todo] == [p[0] for p in roadmap["topics"]["arrays"]["problems"][2:]]


def test_a_finished_topic_drops_out_of_the_queue(roadmap):
    solved = {p[0]: meta(p[0]) for p in roadmap["topics"]["two-pointers"]["problems"]}
    names = [name for name, _ in lc_session._next_up(solved, roadmap)]
    assert "Two Pointers" not in names


def test_focus_topics_are_queued_before_the_rest(roadmap):
    names = [name for name, _ in lc_session._next_up({}, roadmap)]
    focus_names = [roadmap["topics"][k]["name"] for k in roadmap["focus"]]
    assert names[:len(focus_names)] == focus_names


def test_progress_counts_only_topics_with_problems(roadmap):
    rows = lc_session._progress({}, roadmap)
    assert all(total > 0 for _, _, total in rows)
    assert ("Two Pointers", 0, 5) in rows


# ------------------------------------------------------------------ time budget


@pytest.mark.parametrize("minutes", [20, 60, 90, 120, 240])
def test_block_minutes_stay_sane_at_every_length(minutes):
    mins = {k: max(2, round(minutes * w)) for k, w in lc_session.WEIGHTS.items()}
    assert all(v >= 2 for v in mins.values())
    assert sum(mins.values()) <= minutes + 8


def test_the_weights_are_a_whole_session():
    assert sum(lc_session.WEIGHTS.values()) == pytest.approx(1.0)
