# 11. Container With Most Water

[Problem on LeetCode](https://leetcode.com/problems/container-with-most-water/)

| | |
|---|---|
| **Difficulty** | 🟡 Medium |
| **Topics** | `Array`, `Two Pointers`, `Greedy` |
| **Time to solve** | — |
| **Attempts** | 1 |
| **Solved** | 2026-09-13 |
| **Unaided** | yes |

## My approach

Solved it unaided. Two honest notes to myself:

**1. I reached for two pointers because of the section header, not because of the problem.**
That's a crutch that isn't there in an interview, so here's the tell I *should* have fired on:

> **"Choose two elements, maximise some function of the pair"** + `n = 100,000`.

The pair framing plus a size that rules out `O(n²)` (10^10 operations) means the answer is
either sorting, a hash map, or converging pointers. It's not a *value* question (so no hash
map) and sorting destroys the positions the width depends on — so: converging pointers,
`left` and `right`, and the only remaining question is which one to move.

**2. Got the width wrong first: `right - left`, not `right - left + 1`.**
`+1` counts *elements in an inclusive range*. This isn't counting bars, it's measuring the
**gap between two walls** — the water sits between them, not on them. Two adjacent bars hold
width 1, not 2. Quick check against Example 2, `[2,2,2]`: best is indices 0 and 2 →
`2 × min(2,2) = 4`. ✓ With `+1` it'd say 6.

## Complexity

**Time:** `O(n)` — each pointer moves at most `n` steps  
**Space:** `O(1)`

## Explanation

### The formula

```
area = (right - left) × min(heights[left], heights[right])
```

Width is the **span between** the walls, and height is the **shorter** of the two — water
pours over the lower wall, so the taller one is wasted above that line. Both halves of that
sentence are where this problem gets you: `+1` on the width, or `max` instead of `min`.

### Why moving the shorter wall is safe

This is the same discard argument as [[0167 Two Sum II - Input Array Is Sorted]], and it's
worth being able to say out loud.

Say `heights[left] ≤ heights[right]`. Ask: **could `left` be part of a better container than
the one we just measured?** Any other partner for `left` lies strictly inside `right`, so:

- its **width** is smaller than `right - left`, and
- its **height** is at most `heights[left]`, because `left` is already the shorter wall and
  the `min` can never exceed it.

Smaller width, no more height ⇒ strictly worse. So `left` is dead and we advance past it.
Every step permanently eliminates one wall and can never eliminate the optimum, so `n` steps
settle it.

**The trap this rules out:** the instinct to chase the tallest bar. Height is capped by the
*shorter* wall, so a tall bar is worth nothing without a tall partner far away — you can't
decide from one side.

When the two are equal, either move works: both walls are capped at the same height, so both
are dead by the same argument.

### Why not sort

Sorting is the reflex on "maximise over pairs", and it's wrong here: the answer depends on
**where** the bars are, and sorting throws the indices away. Worth noticing as a tell — if a
problem's value depends on position, sorting is usually off the table.

### Related

[[0125 Valid Palindrome]] and [[0167 Two Sum II - Input Array Is Sorted]] are the same
machinery. The natural follow-up is **42. Trapping Rain Water** — same array, same two
pointers, but it accumulates water at every index instead of maximising one container.

## Mistakes / what to remember

- **Width is `right - left`.** No `+1` — you're measuring the gap *between* two walls, not
  counting elements in an inclusive range. `+1` belongs to counting problems, not spans.
- **Height is `min` of the two walls**, never `max` — water pours over the lower one.
- **The tell I missed: "pick two elements, maximise a function of the pair" with
  `n = 100,000`.** The pair framing plus a size that rules out `O(n²)` is the converging-
  pointer signature. *Knowing it from the section header doesn't count.*
- **Always ask which pointer to move, and justify it with the discard argument:** the shorter
  wall's best remaining container is narrower *and* no taller, so it can't win. Same sentence
  shape as 167 and 3Sum.
- **Don't sort when the answer depends on position.** Sorting destroys the widths.
- Chasing the tallest bar fails — height is capped by the shorter side, so one bar tells you
  nothing on its own.

## Solution

See [`solution.py`](./solution.py).
