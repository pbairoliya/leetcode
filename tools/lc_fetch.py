"""lc_fetch.py — resolve a problem reference to structured problem data.

Talks to LeetCode's public GraphQL endpoint (no auth needed for problem text)
and converts the HTML description into Markdown with the stdlib HTML parser,
so this file has zero third-party dependencies.
"""
from __future__ import annotations

import difflib
import html
import json
import re
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from typing import Any

from lccore import LcError, config, log, slugify

GRAPHQL_URL = "https://leetcode.com/graphql"
PROBLEM_INDEX_URL = "https://leetcode.com/api/problems/all/"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) lc-cli"
INDEX_TTL = 7 * 24 * 3600

QUESTION_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    questionFrontendId
    title
    titleSlug
    difficulty
    content
    likes
    dislikes
    isPaidOnly
    topicTags { name slug }
    codeSnippets { lang langSlug code }
    hints
    stats
  }
}
"""


# --------------------------------------------------------------------------- http


def _post_json(url: str, payload: dict[str, Any], timeout: int = 20) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "Referer": "https://leetcode.com/",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _get_json(url: str, timeout: int = 20) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _retrying(fn, *args, attempts: int = 3, **kwargs):
    """LeetCode rate-limits bursts; back off rather than failing the command."""
    last: Exception | None = None
    for i in range(attempts):
        try:
            return fn(*args, **kwargs)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            last = exc
            if i < attempts - 1:
                time.sleep(1.5 * (i + 1))
    raise LcError(f"network request failed after {attempts} tries: {last}")


# --------------------------------------------------------------------------- slug index


def _index_path():
    return config().cache_dir / "problem-index.json"


def problem_index(refresh: bool = False) -> list[dict[str, Any]]:
    """All {id, slug, title, difficulty}, cached for a week.

    Needed because sites like NeetCode use their own slugs
    ('reverse-a-linked-list' vs LeetCode's 'reverse-linked-list'), so a direct
    slug lookup is not always enough.
    """
    path = _index_path()
    if not refresh and path.exists() and (time.time() - path.stat().st_mtime) < INDEX_TTL:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    raw = _retrying(_get_json, PROBLEM_INDEX_URL)
    levels = {1: "Easy", 2: "Medium", 3: "Hard"}
    index = [
        {
            "id": str(p["stat"]["frontend_question_id"]),
            "slug": p["stat"]["question__title_slug"],
            "title": p["stat"]["question__title"],
            "difficulty": levels.get((p.get("difficulty") or {}).get("level"), "Unknown"),
            "paid": bool(p.get("paid_only")),
        }
        for p in raw.get("stat_status_pairs", [])
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index), encoding="utf-8")
    return index


def resolve_slug(slug: str | None, pid: str | None) -> str:
    """Map a possibly-foreign slug or a problem number onto a real LeetCode slug."""
    if slug and not pid:
        # The common case: the slug is already correct. Trust it and let the
        # GraphQL call be the validator, so we avoid downloading the index.
        return slug
    index = problem_index()
    if pid:
        for row in index:
            if row["id"] == str(int(pid)):
                return row["slug"]
        raise LcError(f"no LeetCode problem numbered {pid}")
    raise LcError("nothing to resolve")


ALIAS_PATH = __import__("pathlib").Path(__file__).resolve().parent / "aliases.json"


def load_aliases() -> dict[str, str]:
    """Foreign slug -> LeetCode slug.

    NeetCode renames a lot of problems ('duplicate-integer' is LeetCode's
    'contains-duplicate'), and those renames share no words, so no amount of
    fuzzy matching finds them. The table is checked in; `lc alias` extends it.
    """
    try:
        return json.loads(ALIAS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_alias(foreign: str, leetcode: str) -> None:
    aliases = load_aliases()
    aliases[foreign] = leetcode
    ALIAS_PATH.write_text(json.dumps(dict(sorted(aliases.items())), indent=2) + "\n", encoding="utf-8")


def slug_candidates(slug: str, limit: int = 5) -> list[dict[str, Any]]:
    """Best index matches for an unknown slug, best first."""
    index = problem_index()
    stop = {"a", "an", "the", "of", "in", "to", "and"}
    want = set(slug.split("-")) - stop
    scored = []
    for row in index:
        have = set(row["slug"].split("-")) - stop
        if not have:
            continue
        jaccard = len(want & have) / len(want | have) if want else 0.0
        ratio = difflib.SequenceMatcher(None, slug, row["slug"]).ratio()
        scored.append((max(jaccard, ratio * 0.95), row))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [dict(row, score=round(score, 3)) for score, row in scored[:limit]]


# Below this similarity we refuse to guess: silently opening the wrong problem
# is far worse than making the user retype a slug.
CONFIDENT = 0.82


def _resolve_unknown_slug(slug: str) -> str:
    alias = load_aliases().get(slug)
    if alias:
        log(f"alias: {slug!r} -> {alias!r}")
        return alias

    candidates = slug_candidates(slug)
    if candidates and candidates[0]["score"] >= CONFIDENT:
        best = candidates[0]
        log(f"resolved {slug!r} -> {best['slug']!r} ({best['title']})")
        return best["slug"]

    lines = [f"could not identify {slug!r} on LeetCode. Closest matches:"]
    lines += [f"    {c['slug']:<45} {c['title']} ({c['difficulty']})" for c in candidates]
    lines.append(f"  If one is right:  lc alias {slug} <leetcode-slug>")
    raise LcError("\n".join(lines))


# --------------------------------------------------------------------------- html -> markdown


class _Html2Md(HTMLParser):
    """Small, targeted converter for LeetCode's description HTML.

    LeetCode uses a narrow tag vocabulary (p, pre, code, strong, em, ul/ol/li,
    sup, sub, img, br), so a full markdown library would be overkill.
    """

    BLOCK = {"p", "div", "pre", "ul", "ol", "li", "blockquote", "h1", "h2", "h3", "h4"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.in_pre = 0
        self.list_stack: list[str] = []
        self.li_index: list[int] = []

    def _emit(self, text: str) -> None:
        self.out.append(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "pre":
            self.in_pre += 1
            self._emit("\n\n```\n")
        elif self.in_pre and tag == "br":
            self._emit("\n")
        elif self.in_pre:
            pass  # no inline markup inside a fenced block
        elif tag == "code":
            self._emit("`")
        elif tag in ("strong", "b"):
            self._emit("**")
        elif tag in ("em", "i"):
            self._emit("*")
        elif tag == "sup":
            self._emit("^")
        elif tag == "sub":
            self._emit("_")
        elif tag == "br":
            self._emit("  \n")
        elif tag in ("ul", "ol"):
            self.list_stack.append(tag)
            self.li_index.append(0)
            self._emit("\n")
        elif tag == "li":
            if self.list_stack:
                depth = "  " * (len(self.list_stack) - 1)
                if self.list_stack[-1] == "ol":
                    self.li_index[-1] += 1
                    self._emit(f"\n{depth}{self.li_index[-1]}. ")
                else:
                    self._emit(f"\n{depth}- ")
        elif tag == "img" and a.get("src"):
            self._emit(f"\n![{a.get('alt', '')}]({a['src']})\n")
        elif tag == "a" and a.get("href"):
            self._emit("[")
        elif tag in self.BLOCK:
            self._emit("\n\n")

    def handle_endtag(self, tag):
        if tag == "pre":
            self.in_pre = max(0, self.in_pre - 1)
            self._emit("\n```\n\n")
        elif self.in_pre:
            pass
        elif tag == "code":
            self._emit("`")
        elif tag in ("strong", "b"):
            self._emit("**")
        elif tag in ("em", "i"):
            self._emit("*")
        elif tag == "li":
            pass  # closing an <li> must not open a blank line before the next
        elif tag in ("ul", "ol"):
            if self.list_stack:
                self.list_stack.pop()
                self.li_index.pop()
            self._emit("\n")
        elif tag == "a":
            self._emit("]")
        elif tag in self.BLOCK:
            self._emit("\n")

    def handle_data(self, data):
        if self.in_pre:
            self._emit(data)
        else:
            # Collapse the newlines LeetCode's HTML is pretty-printed with,
            # but keep intentional spacing between words.
            self._emit(re.sub(r"\s+", " ", data))

    def result(self) -> str:
        text = "".join(self.out)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"```\n{2,}", "```\n", text)
        return text.strip()


def html_to_markdown(content: str | None) -> str:
    if not content:
        return ""
    parser = _Html2Md()
    parser.feed(html.unescape(content) if "&lt;" in content else content)
    parser.close()
    return parser.result()


def split_sections(markdown: str) -> dict[str, str]:
    """Pull Examples, Constraints and Follow-up out of the description body.

    LeetCode marks them with bold headings ('**Example 1:**', '**Constraints:**'),
    which is stable enough to split on and reads far better in a note.
    Order matters: constraints trail the examples, and the follow-up trails the
    constraints, so we peel them off from the bottom up.
    """
    constraints = ""
    m = re.search(r"\*\*\s*Constraints:?\s*\*\*", markdown)
    if m:
        constraints = markdown[m.end():].strip()
        markdown = markdown[: m.start()].strip()

    follow_up = ""
    for haystack_name in ("constraints", "markdown"):
        haystack = constraints if haystack_name == "constraints" else markdown
        fu = re.search(r"\*\*\s*Follow[- ]?up:?\s*\*\*", haystack)
        if fu:
            follow_up = haystack[fu.end():].strip()
            if haystack_name == "constraints":
                constraints = haystack[: fu.start()].strip()
            else:
                markdown = haystack[: fu.start()].strip()
            break

    examples = ""
    m = re.search(r"\*\*\s*Example 1:?\s*\*\*", markdown)
    if m:
        examples = markdown[m.start():].strip()
        markdown = markdown[: m.start()].strip()

    return {
        "description": markdown.strip(),
        "examples": examples.strip(),
        "constraints": constraints.strip(),
        "follow_up": follow_up.strip(),
    }


# --------------------------------------------------------------------------- fetch


def _cache_path(slug: str):
    return config().cache_dir / f"{slug}.json"


def fetch_question(slug: str, refresh: bool = False) -> dict[str, Any]:
    cache = _cache_path(slug)
    if not refresh and cache.exists():
        try:
            return json.loads(cache.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    data = _retrying(_post_json, GRAPHQL_URL, {
        "query": QUESTION_QUERY,
        "variables": {"titleSlug": slug},
        "operationName": "questionData",
    })
    question = (data.get("data") or {}).get("question")
    if not question:
        raise LcError(f"LeetCode has no problem with slug {slug!r}")
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(question), encoding="utf-8")
    return question


def starter_code(question: dict[str, Any]) -> str:
    code = ""
    for snippet in question.get("codeSnippets") or []:
        if snippet.get("langSlug") == "python3":
            code = snippet.get("code", "").strip()
            break
    if not code:
        return "class Solution:\n    def solve(self):\n        pass"
    # Snippets end on a bare `def ...:` signature, which is a SyntaxError as-is.
    if code.rstrip().endswith(":"):
        last = code.rstrip().split("\n")[-1]
        indent = " " * (len(last) - len(last.lstrip()) + 4)
        code += f"\n{indent}pass"
    return code


def acceptance(question: dict[str, Any]) -> str:
    try:
        return json.loads(question.get("stats") or "{}").get("acRate", "")
    except json.JSONDecodeError:
        return ""


def get_problem(target: str, refresh: bool = False) -> dict[str, Any]:
    """Full pipeline: user input -> normalized problem dict for the renderer."""
    from lccore import parse_target

    slug, pid = parse_target(target)
    slug = resolve_slug(slug, pid) if pid else slug
    assert slug

    slug = load_aliases().get(slug, slug)
    try:
        question = fetch_question(slug, refresh=refresh)
    except LcError:
        slug = _resolve_unknown_slug(slug)
        question = fetch_question(slug, refresh=refresh)

    body = split_sections(html_to_markdown(question.get("content")))
    return {
        "id": question.get("questionFrontendId") or question.get("questionId") or "0000",
        "title": question.get("title") or slug.replace("-", " ").title(),
        "slug": question.get("titleSlug") or slug,
        "difficulty": (question.get("difficulty") or "Unknown").capitalize(),
        "link": f"https://leetcode.com/problems/{question.get('titleSlug') or slug}/",
        "topics": [t["name"] for t in question.get("topicTags") or []],
        "paid_only": bool(question.get("isPaidOnly")),
        "hints": question.get("hints") or [],
        "acceptance": acceptance(question),
        "starter": starter_code(question),
        **body,
    }


def stub_problem(target: str) -> dict[str, Any]:
    """Offline fallback so `lc new` never leaves you without a note."""
    from lccore import parse_target

    try:
        slug, pid = parse_target(target)
    except LcError:
        slug, pid = slugify(target), None
    slug = slug or f"problem-{pid}"
    return {
        "id": pid or "0000",
        "title": slug.replace("-", " ").title(),
        "slug": slug,
        "difficulty": "Unknown",
        "link": target if target.startswith("http") else f"https://leetcode.com/problems/{slug}/",
        "topics": [],
        "paid_only": False,
        "hints": [],
        "acceptance": "",
        "starter": "class Solution:\n    def solve(self):\n        pass",
        "follow_up": "",
        "description": "_Offline — problem text could not be fetched. Run `lc refresh` later._",
        "examples": "",
        "constraints": "",
    }
