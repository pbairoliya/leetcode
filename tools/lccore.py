"""lccore.py — config, frontmatter and note-file plumbing shared by every lc command.

Deliberately stdlib-only: this runs from launchd and from inside Obsidian's
Node shell, where a virtualenv is not guaranteed to be on PATH.
"""
from __future__ import annotations

import datetime as dt
import os
import re
import subprocess
import sys
import tempfile
try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - guarded by `lc`'s interpreter pick
    raise SystemExit(
        f"lc needs Python 3.11+ for tomllib, but this is {sys.version.split()[0]}.\n"
        "Run commands through `lc`, which picks a suitable interpreter, or set LC_PYTHON."
    )
import unicodedata
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent
REPO_DIR = TOOLS_DIR.parent

DIFFICULTIES = ("Easy", "Medium", "Hard")
NOTE_TYPE = "leetcode"

# Marker pair used for every machine-regenerated block, in notes and READMEs.
# Anything outside the markers is the user's and is never touched.
GEN_BEGIN = "<!-- lc:begin -->"
GEN_END = "<!-- lc:end -->"


class LcError(RuntimeError):
    """Anything the CLI should report as a clean one-line failure."""


# --------------------------------------------------------------------------- config


def _expand(value: str) -> Path:
    return Path(os.path.expanduser(os.path.expandvars(value)))


class Config:
    def __init__(self, data: dict[str, Any]):
        vault = data.get("vault", {})
        repo = data.get("repo", {})
        sync = data.get("sync", {})

        self.vault_dir = _expand(os.environ.get("LC_VAULT_DIR") or vault["dir"])
        self.notes_dir = self.vault_dir / (
            os.environ.get("LC_NOTES_DIR") or vault.get("notes_dir", "Learnings/Leetcode")
        )
        self.vault_name = os.environ.get("LC_VAULT_NAME") or vault.get(
            "name", self.vault_dir.name
        )
        self.repo_dir = _expand(os.environ.get("LC_REPO_DIR") or repo.get("dir", str(REPO_DIR)))
        self.remote = repo.get("remote", "")
        self.branch = repo.get("branch", "main")
        self.publish_statuses = set(sync.get("publish_statuses", ["solved", "review"]))
        self.review_ladder = {
            k.lower(): v for k, v in data.get("review", {}).items()
        } or {"easy": [3, 10, 30, 90], "medium": [2, 7, 21, 60], "hard": [1, 4, 14, 45]}

    @property
    def cache_dir(self) -> Path:
        return self.repo_dir / ".cache"


_config: Config | None = None


def config() -> Config:
    """Load config.toml once. Falls back to config.example.toml so a fresh
    clone still runs before the user has copied the file."""
    global _config
    if _config is not None:
        return _config
    for name in ("config.toml", "config.example.toml"):
        path = REPO_DIR / name
        if path.exists():
            _config = Config(tomllib.loads(path.read_text(encoding="utf-8")))
            return _config
    raise LcError(f"no config.toml or config.example.toml in {REPO_DIR}")


# --------------------------------------------------------------------------- io


def write_atomic(path: Path, text: str) -> bool:
    """Write only if the content actually changed. Returns True if it wrote.

    The no-op-on-identical-content check is what makes `lc sync` idempotent,
    and it keeps iCloud from re-uploading notes we did not change.
    """
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".lc-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    return True


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


# --------------------------------------------------------------------------- slugs


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text


def sanitize_filename(title: str) -> str:
    """Obsidian forbids these in file names; everything else is fair game."""
    return re.sub(r'[\\/:*?"<>|#^\[\]]', "", title).strip() or "Untitled"


def parse_target(target: str) -> tuple[str | None, str | None]:
    """Turn whatever the user pasted into (slug, problem_id).

    Accepts a full leetcode.com or neetcode.io URL (with or without the
    /description/ and /submissions/ suffixes LeetCode appends), a bare slug,
    or a numeric problem id.
    """
    target = target.strip().strip("<>").rstrip("/")
    if not target:
        raise LcError("empty problem target")
    if target.isdigit():
        return None, str(int(target))
    m = re.search(r"(?:leetcode\.com|leetcode\.cn|neetcode\.io)/problems/([^/?#]+)", target, re.I)
    if m:
        return m.group(1).lower(), None
    if re.fullmatch(r"[a-z0-9][a-z0-9-]*", target, re.I):
        return target.lower(), None
    raise LcError(f"could not read a problem slug out of: {target!r}")


# --------------------------------------------------------------------------- frontmatter


_SCALAR_NEEDS_QUOTES = re.compile(r'^\s*$|^[\[\]{}&*!|>%@`#-]|[:#]\s|^\d|^(true|false|null|yes|no)$', re.I)


def _fmt_scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    if _SCALAR_NEEDS_QUOTES.search(s) or '"' in s:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def _parse_scalar(raw: str) -> Any:
    raw = raw.strip()
    if not raw:
        return None
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    low = raw.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "~"):
        return None
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [_parse_scalar(x) for x in inner.split(",")] if inner else []
    return raw


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse the leading --- block. Supports the flat scalar/list shape our
    notes use; anything more exotic is preserved verbatim as a string."""
    if not text.startswith("---"):
        return {}, text
    lines = text.split("\n")
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), None)
    if end is None:
        return {}, text

    meta: dict[str, Any] = {}
    key: str | None = None
    for line in lines[1:end]:
        if not line.strip():
            continue
        item = re.match(r"^\s*-\s*(.*)$", line)
        if item and key is not None and isinstance(meta.get(key), list):
            meta[key].append(_parse_scalar(item.group(1)))
            continue
        kv = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if not kv:
            continue
        key, raw = kv.group(1), kv.group(2)
        meta[key] = [] if raw.strip() == "" and not raw else _parse_scalar(raw)
        if raw.strip() == "":
            meta[key] = None  # may be promoted to a list by a following "- item"
    # Promote keys whose value is None but that were followed by list items.
    return _repair_lists(lines[1:end], meta), "\n".join(lines[end + 1 :]).lstrip("\n")


def _repair_lists(fm_lines: list[str], meta: dict[str, Any]) -> dict[str, Any]:
    key: str | None = None
    for line in fm_lines:
        kv = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if kv:
            key = kv.group(1)
            continue
        if re.match(r"^\s*-\s*", line) and key:
            if not isinstance(meta.get(key), list):
                meta[key] = []
            meta[key].append(_parse_scalar(re.sub(r"^\s*-\s*", "", line)))
    return meta


# Stable key order so a re-render never produces a spurious diff.
FM_ORDER = [
    "type", "title", "slug", "id", "link", "difficulty", "topics", "status",
    "date", "started_at", "ended_at", "time_spent_min", "attempts", "solves",
    "solved_without_help", "next_review", "tags",
]


def dump_frontmatter(meta: dict[str, Any]) -> str:
    keys = [k for k in FM_ORDER if k in meta] + [k for k in meta if k not in FM_ORDER]
    out = ["---"]
    for k in keys:
        v = meta[k]
        if isinstance(v, list):
            out.append(f"{k}:")
            out.extend(f"  - {_fmt_scalar(i)}" for i in v)
            if not v:
                out[-1:] = [f"{k}: []"]
        else:
            out.append(f"{k}: {_fmt_scalar(v)}".rstrip())
    out.append("---")
    return "\n".join(out)


def compose(meta: dict[str, Any], body: str) -> str:
    return dump_frontmatter(meta) + "\n\n" + body.strip() + "\n"


# --------------------------------------------------------------------------- notes


def notes_dir() -> Path:
    d = config().notes_dir
    if not d.exists():
        raise LcError(f"notes folder does not exist: {d}")
    return d


def iter_notes() -> list[tuple[Path, dict[str, Any], str]]:
    """Every lc-managed note in the vault, newest-modified first."""
    out = []
    for path in sorted(notes_dir().rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        meta, body = split_frontmatter(text)
        if meta.get("type") == NOTE_TYPE:
            out.append((path, meta, body))
    out.sort(key=lambda t: t[0].stat().st_mtime, reverse=True)
    return out


def find_note(target: str | None) -> tuple[Path, dict[str, Any], str]:
    """Resolve a slug / id / title fragment to one note.

    With no target, picks the most recently modified unsolved note — which is
    almost always the problem you are sitting on right now.
    """
    notes = iter_notes()
    if not notes:
        raise LcError("no leetcode notes found yet — run `lc new <url>` first")
    if not target:
        unsolved = [n for n in notes if n[1].get("status") not in ("solved", "review")]
        return (unsolved or notes)[0]

    slug, pid = (None, None)
    try:
        slug, pid = parse_target(target)
    except LcError:
        pass
    needle = (slug or target).lower()

    for path, meta, body in notes:
        if pid and str(meta.get("id")) == pid:
            return path, meta, body
        if slug and str(meta.get("slug", "")).lower() == slug:
            return path, meta, body
    matches = [n for n in notes if needle in n[0].stem.lower() or needle in str(n[1].get("slug", "")).lower()]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise LcError(f"no note matches {target!r}")
    names = ", ".join(m[0].stem for m in matches[:6])
    raise LcError(f"{target!r} matches several notes: {names}")


# --------------------------------------------------------------------------- time


def now() -> dt.datetime:
    return dt.datetime.now().replace(microsecond=0)


def parse_ts(value: Any) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(str(value))
    except ValueError:
        return None


def fmt_duration(minutes: int | None) -> str:
    if not minutes:
        return "—"
    h, m = divmod(int(minutes), 60)
    return f"{h}h {m}m" if h else f"{m}m"


def problem_dirname(meta: dict[str, Any]) -> str:
    pid = str(meta.get("id") or "0000")
    pid = pid.zfill(4) if pid.isdigit() else slugify(pid)
    return f"{pid}-{meta.get('slug') or slugify(str(meta.get('title', 'problem')))}"


def problem_dir(meta: dict[str, Any]) -> Path:
    difficulty = str(meta.get("difficulty") or "Unknown").capitalize()
    if difficulty not in DIFFICULTIES:
        difficulty = "Unknown"
    return config().repo_dir / difficulty / problem_dirname(meta)


def obsidian_uri(path: Path) -> str:
    from urllib.parse import quote

    rel = path.relative_to(config().vault_dir).with_suffix("")
    return (
        f"obsidian://open?vault={quote(config().vault_name)}&file={quote(str(rel))}"
    )


def open_in_obsidian(path: Path) -> None:
    try:
        subprocess.run(["open", obsidian_uri(path)], check=False, timeout=10)
    except (OSError, subprocess.SubprocessError) as exc:
        log(f"could not open Obsidian: {exc}")
