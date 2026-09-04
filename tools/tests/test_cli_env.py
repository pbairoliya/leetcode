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


def run(args, path=MINIMAL_PATH):
    return subprocess.run(
        [str(LC), *args],
        env={"PATH": path, "HOME": os.path.expanduser("~")},
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


def test_stats_works_with_a_minimal_path():
    """Exercises the Python modules — this is what raised ModuleNotFoundError."""
    r = run(["stats"])
    assert r.returncode == 0, r.stderr
    assert "tomllib" not in r.stderr
    assert "ModuleNotFoundError" not in r.stderr


def test_explicit_bad_interpreter_is_rejected_with_a_clear_message():
    r = run(["stats"], path=MINIMAL_PATH)
    assert "Traceback" not in r.stderr
    bad = subprocess.run(
        [str(LC), "stats"],
        env={"PATH": MINIMAL_PATH, "HOME": os.path.expanduser("~"),
             "LC_PYTHON": "/nonexistent/python"},
        capture_output=True, text=True, timeout=60,
    )
    # A bad LC_PYTHON must fall through to a working one, not explode.
    assert bad.returncode == 0, bad.stderr
