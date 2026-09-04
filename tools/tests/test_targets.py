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
