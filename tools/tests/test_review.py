"""The nightly reading doc, and dropping a problem you've given up on."""
import datetime as dt
import types

import lc_cmds
import lc_review
import pytest

TODAY = dt.date(2026, 9, 12)


class FakeConfig:
    publish_statuses = {"solved", "review"}


def note(tmp_path, name, meta, body=""):
    return (tmp_path / name, meta, body)


@pytest.fixture
def vault(monkeypatch):
    """Let a test hand `build()` an exact set of notes."""
    monkeypatch.setattr(lc_review, "config", lambda: FakeConfig())

    def load(rows):
        monkeypatch.setattr(lc_review, "iter_notes", lambda: rows)
    return load


SOLVED_TODAY = {
    "id": "347", "title": "Top K Frequent Elements", "difficulty": "Medium",
    "status": "solved", "date": "2026-09-12", "time_spent_min": 8, "attempts": 1,
}
BODY = (
    "## My approach\n\nBucket the counts.\n\n"
    "## Solution\n\n```python\nreturn []\n```\n\n"
    "## Complexity\n\n**Time:** `O(n)`\n\n"
    "## Mistakes / what to remember\n\n- off by one on the bucket count\n"
)


def test_todays_solves_land_in_the_doc(tmp_path, vault):
    vault([note(tmp_path, "0347 Top K.md", SOLVED_TODAY, BODY)])
    meta, body = lc_review.build(TODAY)
    assert meta["solved_today"] == 1
    assert "347. Top K Frequent Elements" in body
    assert "Bucket the counts." in body
    assert "off by one on the bucket count" in body
    assert "[[0347 Top K]]" in body


def test_a_problem_solved_yesterday_is_not_todays_work(tmp_path, vault):
    stale = SOLVED_TODAY | {"date": "2026-09-11"}
    vault([note(tmp_path, "0347 Top K.md", stale, BODY)])
    meta, body = lc_review.build(TODAY)
    assert meta["solved_today"] == 0
    assert "Nothing solved today" in body


def test_unsolved_problems_never_appear(tmp_path, vault):
    vault([note(tmp_path, "0131 Palindrome.md", {
        "id": "131", "title": "Palindrome Partitioning", "status": "abandoned",
        "date": "2026-09-12", "difficulty": "Medium",
    }, BODY)])
    meta, _ = lc_review.build(TODAY)
    assert meta["solved_today"] == 0


def test_review_is_due_on_and_after_its_date(tmp_path, vault):
    rows = [
        note(tmp_path, "A.md", SOLVED_TODAY | {
            "id": "1", "date": "2026-09-02", "next_review": "2026-09-12"}, BODY),
        note(tmp_path, "B.md", SOLVED_TODAY | {
            "id": "2", "date": "2026-09-02", "next_review": "2026-09-01"}, BODY),
        note(tmp_path, "C.md", SOLVED_TODAY | {
            "id": "3", "date": "2026-09-02", "next_review": "2026-09-13"}, BODY),
    ]
    vault(rows)
    meta, body = lc_review.build(TODAY)
    assert meta["due_count"] == 2
    assert "[[C]]" not in body


def test_a_problem_solved_today_is_not_also_listed_as_due(tmp_path, vault):
    vault([note(tmp_path, "0347 Top K.md",
                SOLVED_TODAY | {"next_review": "2026-09-12"}, BODY)])
    meta, body = lc_review.build(TODAY)
    assert meta["solved_today"] == 1
    assert meta["due_count"] == 0
    assert "Nothing due" in body


def test_the_doc_always_transcludes_the_pattern_sheet(tmp_path, vault):
    vault([])
    _, body = lc_review.build(TODAY)
    assert f"![[{lc_review.PATTERNS_NOTE}]]" in body


def test_time_at_the_keyboard_is_summed(tmp_path, vault):
    vault([
        note(tmp_path, "A.md", SOLVED_TODAY | {"id": "1", "time_spent_min": 8}, BODY),
        note(tmp_path, "B.md", SOLVED_TODAY | {"id": "2", "time_spent_min": 37}, BODY),
    ])
    _, body = lc_review.build(TODAY)
    assert "45m" in body


# --------------------------------------------------------------------------- drop


@pytest.fixture
def dropped(monkeypatch, tmp_path):
    """Run `lc drop` against an in-memory note and hand back the saved metadata."""
    def run(meta):
        saved = {}
        monkeypatch.setattr(lc_cmds, "find_note",
                            lambda target: (tmp_path / "n.md", meta, "body"))
        monkeypatch.setattr(lc_cmds, "_save",
                            lambda p, m, b: saved.update(m))
        monkeypatch.setattr(lc_cmds, "_refresh_stats", lambda m, b: b)
        lc_cmds.cmd_drop(types.SimpleNamespace(target=None))
        return saved
    return run


def test_drop_banks_the_running_clock_and_stops_it(dropped):
    started = (lc_cmds.now() - dt.timedelta(minutes=25)).isoformat()
    meta = dropped({"title": "X", "started_at": started, "time_spent_min": 5})
    assert meta["status"] == "abandoned"
    assert meta["started_at"] is None
    assert meta["time_spent_min"] == 30


def test_dropping_an_unstarted_problem_keeps_its_banked_time(dropped):
    meta = dropped({"title": "X", "started_at": None, "time_spent_min": 12})
    assert meta["status"] == "abandoned"
    assert meta["time_spent_min"] == 12
