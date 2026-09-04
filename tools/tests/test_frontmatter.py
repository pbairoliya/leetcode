"""Frontmatter must survive a read/write round trip untouched — every command
rewrites the note, so a lossy parser would quietly corrupt the vault."""
import lccore


def test_round_trip_preserves_values():
    text = (
        "---\n"
        "type: leetcode\n"
        'title: "Two Sum"\n'
        "id: 1\n"
        "topics:\n  - Array\n  - Hash Table\n"
        "time_spent_min: 37\n"
        "solved_without_help: true\n"
        "started_at:\n"
        "---\n\n"
        "# body\n"
    )
    meta, body = lccore.split_frontmatter(text)
    assert meta["title"] == "Two Sum"
    assert meta["id"] == 1
    assert meta["topics"] == ["Array", "Hash Table"]
    assert meta["time_spent_min"] == 37
    assert meta["solved_without_help"] is True
    assert meta["started_at"] is None
    assert body.strip() == "# body"

    again, _ = lccore.split_frontmatter(lccore.compose(meta, body))
    assert again == meta


def test_stable_key_order_means_no_spurious_diff():
    meta = {"tags": ["x"], "title": "T", "type": "leetcode", "id": 3}
    once = lccore.dump_frontmatter(meta)
    twice = lccore.dump_frontmatter(lccore.split_frontmatter(once + "\n\nbody")[0])
    assert once == twice
    assert once.index("type:") < once.index("title:") < once.index("tags:")


def test_empty_list_and_colon_in_value():
    meta = {"topics": [], "title": "A: B"}
    parsed, _ = lccore.split_frontmatter(lccore.compose(meta, "x"))
    assert parsed["topics"] == []
    assert parsed["title"] == "A: B"


def test_no_frontmatter_is_left_alone():
    meta, body = lccore.split_frontmatter("# just a heading\n")
    assert meta == {}
    assert body == "# just a heading\n"
