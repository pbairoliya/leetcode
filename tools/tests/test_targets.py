"""Whatever the user pastes has to resolve to a slug."""
import pytest

from lccore import LcError, parse_target


@pytest.mark.parametrize("raw,slug", [
    ("https://leetcode.com/problems/two-sum/", "two-sum"),
    ("https://leetcode.com/problems/two-sum/description/", "two-sum"),
    ("https://leetcode.com/problems/two-sum/submissions/12345/", "two-sum"),
    ("http://leetcode.cn/problems/two-sum", "two-sum"),
    ("https://neetcode.io/problems/duplicate-integer", "duplicate-integer"),
    ("<https://leetcode.com/problems/Two-Sum/>", "two-sum"),
    ("two-sum", "two-sum"),
])
def test_slug_forms(raw, slug):
    assert parse_target(raw)[0] == slug


def test_numeric_id():
    assert parse_target("206") == (None, "206")
    assert parse_target("0206") == (None, "206")


def test_garbage_is_rejected():
    with pytest.raises(LcError):
        parse_target("")
    with pytest.raises(LcError):
        parse_target("https://example.com/not/a/problem")


# --------------------------------------------------------------- local problems


def test_local_problem_keeps_the_neetcode_link():
    import lc_fetch
    p = lc_fetch.local_problem(
        "https://neetcode.io/problems/queue", "9001",
        title="Design Double-ended Queue", difficulty="easy")
    assert p["link"] == "https://neetcode.io/problems/queue"
    assert p["difficulty"] == "Easy"
    assert p["id"] == "9001"


def test_a_title_beats_neetcodes_generic_slug():
    import lc_fetch
    p = lc_fetch.local_problem("https://neetcode.io/problems/queue", "9001",
                               title="Design Double-ended Queue")
    assert p["slug"] == "design-double-ended-queue"


def test_without_a_title_the_url_slug_is_used():
    import lc_fetch
    p = lc_fetch.local_problem("https://neetcode.io/problems/queue", "9001")
    assert p["slug"] == "queue"
    assert p["title"] == "Queue"


def test_the_link_label_follows_the_host():
    import lc_render
    assert lc_render.source_name("https://neetcode.io/problems/queue") == "NeetCode"
    assert lc_render.source_name("https://leetcode.com/problems/two-sum/") == "LeetCode"


def test_local_ids_start_above_leetcodes_numbering(monkeypatch):
    import lc_cmds
    monkeypatch.setattr(lc_cmds, "iter_notes", lambda: [])
    assert lc_cmds._next_local_id() == "9001"


def test_local_ids_increment_past_the_highest_local_note(monkeypatch):
    import lc_cmds
    rows = [(None, {"id": "9001"}, ""), (None, {"id": "347"}, ""), (None, {"id": "9007"}, "")]
    monkeypatch.setattr(lc_cmds, "iter_notes", lambda: rows)
    assert lc_cmds._next_local_id() == "9008"
