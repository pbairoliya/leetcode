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
| **Solved** | 20 |
| 🟢 Easy | 7 |
| 🟡 Medium | 11 |
| 🔴 Hard | 2 |
| **Median solve time** | 13m |
| **Total time** | 1h 40m |
| **Current streak** | 2 day(s) |
| **Last solved** | 2026-09-16 |

## Topics

`Array ×11` `Two Pointers ×8` `Hash Table ×5` `Stack ×5` `Linked List ×4` `String ×4` `Recursion ×3` `Sliding Window ×3` `Dynamic Programming ×2` `Monotonic Stack ×2` `Heap (Priority Queue) ×2` `Sorting ×2` `Union-Find ×1` `Math ×1` `Bracket Sequences ×1` `Queue ×1` `Monotonic Queue ×1` `Range Minimum/Maximum Query ×1` `Greedy ×1` `Binary Search ×1` `Divide and Conquer ×1` `Bucket Sort ×1` `Counting ×1` `Quickselect ×1`

## Problems

| # | Problem | Difficulty | Time | Attempts | Solved |
|---|---|---|---|---|---|
| 739 | [Daily Temperatures](./Medium/0739-daily-temperatures) | 🟡 Medium | 9m | 2 | 2026-09-16 |
| 150 | [Evaluate Reverse Polish Notation](./Medium/0150-evaluate-reverse-polish-notation) | 🟡 Medium | — | 1 | 2026-09-15 |
| 20 | [Valid Parentheses](./Easy/0020-valid-parentheses) | 🟢 Easy | — | 1 | 2026-09-15 |
| 239 | [Sliding Window Maximum](./Hard/0239-sliding-window-maximum) | 🔴 Hard | — | 1 | 2026-09-15 |
| 567 | [Permutation in String](./Medium/0567-permutation-in-string) | 🟡 Medium | — | 1 | 2026-09-15 |
| 3 | [Longest Substring Without Repeating Characters](./Medium/0003-longest-substring-without-repeating-characters) | 🟡 Medium | — | 1 | 2026-09-15 |
| 42 | [Trapping Rain Water](./Hard/0042-trapping-rain-water) | 🔴 Hard | — | 1 | 2026-09-15 |
| 128 | [Longest Consecutive Sequence](./Medium/0128-longest-consecutive-sequence) | 🟡 Medium | — | 2 | 2026-09-13 |
| 11 | [Container With Most Water](./Medium/0011-container-with-most-water) | 🟡 Medium | — | 1 | 2026-09-13 |
| 15 | [3Sum](./Medium/0015-3sum) | 🟡 Medium | — | 1 | 2026-09-13 |
| 167 | [Two Sum II - Input Array Is Sorted](./Medium/0167-two-sum-ii-input-array-is-sorted) | 🟡 Medium | — | 1 | 2026-09-13 |
| 125 | [Valid Palindrome](./Easy/0125-valid-palindrome) | 🟢 Easy | — | 1 | 2026-09-13 |
| 19 | [Remove Nth Node From End of List](./Medium/0019-remove-nth-node-from-end-of-list) | 🟡 Medium | — | 1 | 2026-09-12 |
| 143 | [Reorder List](./Medium/0143-reorder-list) | 🟡 Medium | 20m | 1 | 2026-09-12 |
| 9001 | [Design Double-ended Queue](./Easy/9001-design-double-ended-queue) | 🟢 Easy | 8m | 1 | 2026-09-12 |
| 347 | [Top K Frequent Elements](./Medium/0347-top-k-frequent-elements) | 🟡 Medium | 8m | 1 | 2026-09-12 |
| 121 | [Best Time to Buy and Sell Stock](./Easy/0121-best-time-to-buy-and-sell-stock) | 🟢 Easy | 18m | 2 | 2026-09-03 |
| 1 | [Two Sum](./Easy/0001-two-sum) | 🟢 Easy | 37m | 2 | 2026-09-03 |
| 21 | [Merge Two Sorted Lists](./Easy/0021-merge-two-sorted-lists) | 🟢 Easy | — | 2 | 2026-09-02 |
| 206 | [Reverse Linked List](./Easy/0206-reverse-linked-list) | 🟢 Easy | — | 2 | 2026-09-02 |

_Updated 2026-09-17 by `lc sync`._

<!-- lc:end -->
