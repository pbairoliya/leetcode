"""The code-reconciliation matrix.

This is the guard that makes "the note is the source of truth" safe: an
untouched starter block must never be allowed to erase a solution written in
the editor, and vice versa.
"""
import lc_render
import lc_sync
import pytest

STARTER = "class Solution:\n    def twoSum(self, nums, target):\n        pass"
REAL = "class Solution:\n    def twoSum(self, nums, target):\n        return [0, 1]"
HEADER = '"""1. Two Sum (Easy)\n\nhttps://x\n"""\nfrom typing import List, Optional  # noqa: F401\n\n\n'


@pytest.mark.parametrize("code", [
    "",
    "   \n\n  ",
    STARTER,
    "class Solution:\n    def f(self):\n        ...",
    "# just a comment\nclass Solution:\n    def f(self):\n        pass",
])
def test_stubs_are_recognised_as_empty(code):
    assert lc_render.is_placeholder_code(code, STARTER)


def test_real_code_is_not_a_stub():
    assert not lc_render.is_placeholder_code(REAL, STARTER)


@pytest.mark.parametrize("header", ['"""one line"""\n', '"""multi\n\nline\n"""\n', ""])
def test_strip_header_handles_every_docstring_shape(header):
    text = header + "from typing import List\n\n\n" + REAL
    assert lc_sync._strip_header(text) == REAL


def _body(code):
    return f"## Solution\n\n```python\n{code}\n```\n\n## Complexity\n\nx\n"


def test_note_wins_when_it_has_real_code(tmp_path):
    f = tmp_path / "solution.py"
    f.write_text(HEADER + "class Solution:\n    def old(self):\n        return 1\n")
    code, source, _ = lc_sync.reconcile_code({}, _body(REAL), f)
    assert source == "note"
    assert code == REAL


def test_file_wins_when_the_note_block_is_a_stub(tmp_path):
    f = tmp_path / "solution.py"
    f.write_text(HEADER + REAL + "\n")
    code, source, new_body = lc_sync.reconcile_code({}, _body(STARTER), f)
    assert source == "file"
    assert code == REAL
    assert REAL in lc_render.extract_code(new_body), "the note is updated to match"


def test_both_empty_is_skipped(tmp_path):
    f = tmp_path / "solution.py"
    f.write_text(HEADER + STARTER + "\n")
    code, source, _ = lc_sync.reconcile_code({}, _body(STARTER), f)
    assert (code, source) == ("", "")


def test_missing_file_falls_back_to_the_note(tmp_path):
    code, source, _ = lc_sync.reconcile_code({}, _body(REAL), tmp_path / "nope.py")
    assert (code, source) == (REAL, "note")


def test_rewriting_the_code_block_does_not_grow_blank_lines():
    """A \\s*$ heading anchor used to swallow the following newlines and re-add
    them, so the gap under '## Solution' grew on every single sync."""
    body = _body(STARTER)
    for _ in range(6):
        body = lc_render.replace_code(body, REAL)
    assert "\n\n\n" not in body
    assert lc_render.extract_code(body) == REAL
