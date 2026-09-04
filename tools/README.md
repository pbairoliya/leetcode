# `lc`

A LeetCode workflow that keeps solving, writing up, and publishing in one loop.

The **Obsidian note is the source of truth.** You solve in the note; `lc sync`
extracts the code into `solution.py` and your prose into a `README.md`, then
commits both. Nothing in the repo is meant to be hand-edited.

## Layout

| File | Role |
|---|---|
| `lc` | bash dispatcher — argument handling, git, launchd, opening Obsidian |
| `lccore.py` | config, frontmatter parsing, note discovery, atomic writes |
| `lc_fetch.py` | LeetCode GraphQL client + HTML→Markdown, no third-party deps |
| `lc_render.py` | problem data → note, and reading sections back out |
| `lc_cmds.py` | `new` / `start` / `pause` / `done` / `refresh` / `migrate` |
| `lc_sync.py` | notes → repo files, code reconciliation, README generation |
| `lc_stats.py` | terminal dashboard, in-flight status, commit subjects |
| `aliases.json` | foreign slug → LeetCode slug (NeetCode renames a lot of problems) |

Python is stdlib-only, because this runs from launchd and from inside
Obsidian's Node shell where a virtualenv isn't guaranteed to be on PATH.

## Commands

Run `lc --help`. Every command that takes a `<problem>` accepts a URL, a slug,
a problem number, or part of the title; omit it and `lc` acts on the problem
you're currently working on.

## The reconciliation rule

`lc sync` has to decide whether the note's code block or `solution.py` is
authoritative. In order:

1. The note's block has real code → **the note wins**, written to `solution.py`.
2. The note's block is still the starter stub, but the file has real code →
   **the file wins**, and the code is written back into the note.
3. Neither has code → the problem is **skipped** with a warning.

Rule 2 is what makes "the note wins" safe: an untouched starter block can never
erase work done in an editor. `tests/test_reconcile.py` covers all four paths.

## Slug resolution

NeetCode and LeetCode don't agree on slugs — NeetCode's `duplicate-integer` is
LeetCode's `contains-duplicate`, and the two share no words, so fuzzy matching
can't bridge it. `lc` tries, in order: the slug as given, `aliases.json`, then a
similarity search against LeetCode's problem index. **If nothing clears the
confidence bar it refuses to guess** and prints the closest candidates, because
silently opening the wrong problem is worse than making you retype. Teach it a
new one with `lc alias <foreign-slug> <leetcode-slug>` — that writes to
`aliases.json`, which is checked in.

## Obsidian setup

Two Templater templates in the vault's `Templates/`:

- **`Leetcode.md`** — prompts for a URL, shells out to `lc new --print`, files
  the note under `Learnings/Leetcode/`. Already bound to **Cmd+L**.
- **`Leetcode Done.md`** — runs `lc done` on the note you're looking at. Bind
  **Cmd+Shift+L** to *Templater: Insert Templates/Leetcode Done.md* (enable the
  template's hotkey in Templater's settings first).

Both are deliberately thin wrappers over the CLI, so the note format lives in
`lc_render.py` alone and can't drift between the terminal and Obsidian.

`Dashboards/LeetCode.base` gives four views: all problems, in flight, due for
review, and by difficulty.

## Scheduling

`lc install` links `lc` into `~/bin` and loads
`com.pbairol.leetcode-sync`, which runs `lc push` at **23:00** with a 09:00
retry in case the Mac slept through it. A clean tree makes a redundant run a
no-op, so firing twice costs nothing. Logs land in `.logs/`.

## Tests

    lc test

Runs offline against a checked-in GraphQL fixture.
