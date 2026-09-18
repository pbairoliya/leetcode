"""`lc` must work under the stripped-down PATH that Obsidian and launchd give it.

Obsidian spawns child processes with launchd's minimal PATH, not your shell
profile's, so `python3` there is macOS's system 3.9 — which has no tomllib.
`lc` therefore picks its own interpreter instead of trusting PATH.
"""
import os
import subprocess
from pathlib import Path

import pytest

LC = Path(__file__).resolve().parents[1] / "lc"
MINIMAL_PATH = "/usr/bin:/bin:/usr/sbin:/sbin"


@pytest.fixture
def vault(tmp_path):
    """A throwaway vault.

    These tests are about the interpreter `lc` picks, not about anyone's notes.
    Pointing them at a real vault made them pass on the author's machine and
    fail everywhere else -- which is exactly the bug CI is for. LC_VAULT_DIR and
    LC_NOTES_DIR override config.toml, so an empty directory is enough.
    """
    notes = tmp_path / "Learnings" / "Leetcode"
    notes.mkdir(parents=True)
    return {"LC_VAULT_DIR": str(tmp_path), "LC_NOTES_DIR": "Learnings/Leetcode"}


def run(args, path=MINIMAL_PATH, env=None):
    return subprocess.run(
        [str(LC), *args],
        env={"PATH": path, "HOME": os.path.expanduser("~"), **(env or {})},
        capture_output=True, text=True, timeout=60,
    )


def test_the_bare_path_python_is_the_one_that_broke():
    """Guards the premise. If PATH's python3 ever gains tomllib this test flips
    to a skip -- but `lc` picking its own interpreter stays correct either way."""
    probe = subprocess.run(
        ["python3", "-c", "import tomllib"],
        env={"PATH": MINIMAL_PATH}, capture_output=True, text=True,
    )
    if probe.returncode == 0:
        pytest.skip("python3 on the minimal PATH already has tomllib")
    assert "No module named 'tomllib'" in probe.stderr


def test_help_works_with_a_minimal_path():
    r = run(["--help"])
    assert r.returncode == 0, r.stderr
    assert "lc new" in r.stdout


def test_stats_works_with_a_minimal_path(vault):
    """Exercises the Python modules — this is what raised ModuleNotFoundError."""
    r = run(["stats"], env=vault)
    assert r.returncode == 0, r.stderr
    assert "tomllib" not in r.stderr
    assert "ModuleNotFoundError" not in r.stderr


def test_explicit_bad_interpreter_is_rejected_with_a_clear_message(vault):
    r = run(["stats"], env=vault)
    assert "Traceback" not in r.stderr
    # A bad LC_PYTHON must fall through to a working one, not explode.
    bad = run(["stats"], env={**vault, "LC_PYTHON": "/nonexistent/python"})
    assert bad.returncode == 0, bad.stderr
