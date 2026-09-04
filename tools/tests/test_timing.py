"""Timer arithmetic and the review ladder."""
import datetime as dt

import lc_cmds
import pytest
from lccore import fmt_duration


def at(minutes_ago):
    return (dt.datetime(2026, 9, 3, 12, 0) - dt.timedelta(minutes=minutes_ago)).isoformat()


NOW = dt.datetime(2026, 9, 3, 12, 0)


def test_elapsed_from_a_running_clock():
    assert lc_cmds._elapsed_min({"started_at": at(37)}, NOW) == 37


def test_elapsed_adds_to_banked_time_across_sittings():
    meta = {"started_at": at(20), "time_spent_min": 45}
    assert lc_cmds._elapsed_min(meta, NOW) == 65


def test_no_clock_keeps_the_banked_total():
    assert lc_cmds._elapsed_min({"time_spent_min": 12}, NOW) == 12
    assert lc_cmds._elapsed_min({}, NOW) == 0


def test_a_clock_from_the_future_never_goes_negative():
    meta = {"started_at": (NOW + dt.timedelta(minutes=5)).isoformat()}
    assert lc_cmds._elapsed_min(meta, NOW) == 0


def test_unparseable_timestamp_is_ignored():
    assert lc_cmds._elapsed_min({"started_at": "not a date", "time_spent_min": 9}, NOW) == 9


@pytest.mark.parametrize("minutes,expected", [
    (0, "—"), (None, "—"), (7, "7m"), (60, "1h 0m"), (95, "1h 35m"), (1440, "24h 0m"),
])
def test_duration_formatting(minutes, expected):
    assert fmt_duration(minutes) == expected


def test_review_ladder_pushes_repeat_solves_further_out():
    today = dt.date(2026, 9, 3)
    first = lc_cmds._next_review({"difficulty": "Medium", "solves": 0}, today)
    third = lc_cmds._next_review({"difficulty": "Medium", "solves": 2}, today)
    assert first < third
    assert first == "2026-09-05"


def test_hard_problems_come_back_sooner_than_easy_ones():
    today = dt.date(2026, 9, 3)
    hard = lc_cmds._next_review({"difficulty": "Hard", "solves": 0}, today)
    easy = lc_cmds._next_review({"difficulty": "Easy", "solves": 0}, today)
    assert hard < easy


def test_ladder_saturates_instead_of_indexing_off_the_end():
    today = dt.date(2026, 9, 3)
    assert lc_cmds._next_review({"difficulty": "Easy", "solves": 99}, today) == "2026-12-02"


def test_zero_duration_reads_as_unknown_not_zero():
    """A 0 means 'no time recorded', so it must not print as '0m'."""
    assert fmt_duration(0) == "—"
    assert fmt_duration(None) == "—"
