# 42. Trapping Rain Water

[Problem on LeetCode](https://leetcode.com/problems/trapping-rain-water/)

| | |
|---|---|
| **Difficulty** | 🔴 Hard |
| **Topics** | `Array`, `Two Pointers`, `Dynamic Programming`, `Stack`, `Monotonic Stack` |
| **Time to solve** | — |
| **Attempts** | 1 |
| **Solved** | 2026-09-15 |
| **Unaided** | yes |

## My approach

Converging pointers again ([[0011 Container With Most Water]]), but the question changed
from *"find the one best container"* to *"add up the water over every single index"*.

The per-index formula is the whole problem:

```
water[i] = min( tallest bar at or left of i , tallest bar at or right of i ) - height[i]
```

Water at `i` is held in by the taller wall on each side, and it spills over the **shorter**
of those two. Do that literally and it's `O(n)` space (two prefix-max arrays). The two-pointer
version gets it to `O(1)` — **you only ever need the smaller of the two maxes, and the
shorter side is the one you already know.**

## Complexity

**Time:** `O(n)`  
**Space:** `O(1)` — the prefix-max array version is `O(n)` space for the same time

## Explanation

### The ordering question

Three statements happen per iteration and there are two ordering constraints. Only **one**
of them can actually break your answer — it's worth knowing which.

#### Constraint 1 (the one that matters): `max` before `total`

```python
leftMax = max(leftMax, height[left])   # first
total += leftMax - height[left]        # then
```

**This order is mandatory.** Swap it and you subtract water that was never there.

Say `leftMax` is `3` and you step onto a bar of height `7`. With the update first,
`leftMax` becomes `7` and the contribution is `7 - 7 = 0` — correct, a wall that tall holds
no water on top of itself. With the update *after*, you compute `3 - 7 = -4` and take four
units **out** of the total.

That's also the quiet elegance of this code: because `leftMax` is refreshed first, it is
always `≥ height[left]`, so the term can never go negative and you don't need a
`max(0, ...)` anywhere. **The `max` isn't just bookkeeping — it's the clamp.**

#### Constraint 2 (the one you asked about): move, then compute

```python
left += 1                              # step onto the new cell
leftMax = max(leftMax, height[left])   # then account for it
```

The mental model that makes this obvious:

> **`left` and `right` are the two walls. The index you move onto is the floor you're
> filling.** So you step onto a cell, *then* pour water into it.

Two things follow:

1. **The starting bars are walls, never floors.** Index `0` has nothing to its left and
   `n-1` has nothing to its right, so neither can hold a drop. Moving first means you never
   try to charge water to them.
2. **`leftMax` is exactly right at the moment you use it.** After `left += 1` and the `max`,
   `leftMax` is the tallest bar in `height[0..left]` *including* `height[left]` — which is
   precisely the left wall for the cell you're standing on. Compute before moving and the
   variable means "the max up to the *previous* cell", which is a different quantity that you
   then have to reason about separately.

Each index gets visited once as "the floor", so every cell is charged exactly once.

#### Does compute-then-move also work?

Yes, as it happens — but by luck, not by structure, and that's why it isn't the version to
write. If you compute first and move after, you charge the two starting indices (both
contribute `0`, since `leftMax == height[0]` there) and you *skip* the index where the
pointers meet. That's harmless only because the pointers always converge on a **tallest** bar:
the shorter side is the one that moves, so a unique global maximum is never stepped off, and
the other pointer walks all the way to it. A tallest bar traps nothing, so the skipped cell
contributes `0` too.

Two separate accidental zeros. Move-then-compute needs no such argument — which is the
point.

### Why the algorithm is correct at all

The part that looks like cheating: `water[i]` needs **both** maxes, but each branch only uses
one of them.

The condition is doing that work. When `height[left] < height[right]` fires, you know there is
a bar of height `height[right]` somewhere to the right — so the right side's true max is at
least that, and it is **not** the binding constraint. `leftMax` is the smaller wall, `min(...)`
resolves to `leftMax`, and you can compute the cell without ever knowing what the right max
turns out to be.

More precisely, the invariant is **`leftMax ≤ rightMax` whenever the left branch runs**
(and the mirror for the right). It holds because `left` only ever advanced past bars that
were shorter than the right wall at that time, and `rightMax` only grows as `right` moves
inward.

**This is the same discard logic as [[0011 Container With Most Water]] and
[[0167 Two Sum II - Input Array Is Sorted]], one level up:** there you asked *"which end can
never be part of a better answer?"*; here you ask *"which end's max is already known to be
the binding one?"* Same answer — the shorter side — and the same reason it's safe to advance.

## Mistakes / what to remember

- **`max` before `total`, always.** Refreshing `leftMax` first guarantees
  `leftMax ≥ height[left]`, so the contribution can never be negative. Compute first and a
  bar taller than everything before it *subtracts* water. **This is the only ordering here
  that can actually produce a wrong answer.**
- **Move, then compute.** `left`/`right` are the two *walls*; the index you step onto is the
  *floor* you're filling. Stepping first keeps `leftMax` meaning "the max including the cell
  I'm standing on", and keeps you off the endpoints, which are walls and can never hold
  water.
- **`water[i] = min(leftMax, rightMax) - height[i]`** — the *shorter* wall decides, because
  water spills over it. Same `min` trap as [[0011 Container With Most Water]].
- **Why one branch can use one max:** the side with the shorter current bar is the binding
  one, and you already know its max. Invariant: `leftMax ≤ rightMax` when the left branch
  runs.
- The `O(n)`-space version (two prefix-max arrays, then one pass) is a fine first answer in
  an interview — say it, then say you can do it in `O(1)` with two pointers.

## Solution

See [`solution.py`](./solution.py).
