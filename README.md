# LeetCode

Solutions and write-ups, plus [`lc`](./tools) — the CLI that generates them.

[![tests](https://github.com/pbairoliya/leetcode/actions/workflows/test.yml/badge.svg)](https://github.com/pbairoliya/leetcode/actions/workflows/test.yml)

## The interesting half is `tools/`

`lc` makes an **Obsidian note the source of truth** for a problem. One command
imports the statement, scaffolds the code, and starts a clock; another stops it,
schedules a spaced-repetition review, and publishes the note into this repo.

```
lc new https://leetcode.com/problems/two-sum/   # import, scaffold, start the clock
                                                # …solve it in your notes…
lc done                                         # stop, mark solved, schedule the review
lc session                                      # a study block built from your own notes
lc push                                         # publish (also runs nightly)
```

The rule worth reading is the reconciliation one. "The note wins" is a nice
thing to say and a dangerous thing to implement — a sync that always trusts the
note will happily overwrite real code with an untouched starter stub. So:

```
note has real code   →  note wins, the repo is rewritten
note has the stub    →  repo wins, and the code is written BACK into the note
neither has code     →  the problem is skipped entirely
```

That middle case is what makes the claim safe, and most of the **94 offline
tests** point at it. No network, no fixtures fetched at runtime — `lc test`
runs in under a second.

A few other decisions that earned their place:

- **Rendering lives in exactly one place.** The Obsidian templates shell out to
  `lc new --print`, so note formatting cannot drift between the terminal and the
  editor.
- **Refuse to guess.** NeetCode uses different slugs than LeetCode
  (`duplicate-integer` is `contains-duplicate`). An unknown slug *fails with
  candidates* rather than fuzzy-matching. A wrong problem silently imported is
  far worse than an error.
- **A study session is derived, not authored.** `lc session` reads your notes and
  builds a timed block: a recall quiz, everything you solved with help, every
  review that is due, and the next problems off a roadmap.

See [`tools/README.md`](./tools/README.md) for the full command reference, and
[`config.example.toml`](./config.example.toml) to point it at your own vault.

## Everything else is generated

Each problem lives in `<Difficulty>/<id>-<slug>/` with the solution and the
notes written while solving it. Editing those by hand is pointless — the next
`lc sync` overwrites them.

<!-- lc:begin -->

## Stats

| Metric | Value |
|---|---|
| **Solved** | 0 |
| 🟢 Easy | 0 |
| 🟡 Medium | 0 |
| 🔴 Hard | 0 |
| **Median solve time** | — |
| **Total time** | — |
| **Current streak** | 0 day(s) |
| **Last solved** | — |

## Problems

| # | Problem | Difficulty | Time | Attempts | Solved |
|---|---|---|---|---|---|

_Updated 2026-09-25 by `lc sync`._

<!-- lc:end -->
