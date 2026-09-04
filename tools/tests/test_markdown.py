"""The HTML->Markdown converter, exercised against a real cached LeetCode payload
so the test runs offline but still reflects the markup LeetCode actually sends."""
import json
from pathlib import Path

import lc_fetch

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "two-sum.json").read_text())


def sections():
    return lc_fetch.split_sections(lc_fetch.html_to_markdown(FIXTURE["content"]))


def test_no_inline_markup_leaks_into_code_fences():
    """LeetCode bolds 'Input:' even inside <pre>; ** there would render literally."""
    examples = sections()["examples"]
    inside = []
    fenced = False
    for line in examples.split("\n"):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            inside.append(line)
    body = "\n".join(inside)
    assert "Input: nums = [2,7,11,15], target = 9" in body
    assert "**" not in body


def test_constraints_are_a_tight_bullet_list():
    constraints = sections()["constraints"]
    lines = [l for l in constraints.split("\n") if l.strip()]
    assert lines == constraints.strip().split("\n"), "no blank lines between bullets"
    assert all(l.startswith("- ") for l in lines)
    assert "2 <= nums.length <= 10^4" in constraints


def test_follow_up_is_split_out_of_constraints():
    s = sections()
    assert "Follow" not in s["constraints"]
    assert "less than `O(n^2)` time complexity" in s["follow_up"]


def test_description_stops_before_the_examples():
    s = sections()
    assert "Example 1" not in s["description"]
    assert "add up to `target`" in s["description"]


def test_starter_code_is_valid_python():
    code = lc_fetch.starter_code(FIXTURE)
    compile(code, "<starter>", "exec")
    assert "twoSum" in code


def test_nested_lists_and_entities():
    md = lc_fetch.html_to_markdown(
        "<p>a &amp; b</p><ul><li>one</li><li>two<ul><li>deep</li></ul></li></ul>"
    )
    assert "a & b" in md
    assert "- one" in md
    assert "  - deep" in md
