# 128. Longest Consecutive Sequence

[Problem on LeetCode](https://leetcode.com/problems/longest-consecutive-sequence/)

| | |
|---|---|
| **Difficulty** | 🟡 Medium |
| **Topics** | `Array`, `Hash Table`, `Union-Find` |
| **Time to solve** | — |
| **Attempts** | 1 |
| **Solved** | 2026-09-13 |
| **Unaided** | no |

## My approach

**Looked at the answer — but I had two of the three pieces.** Worth recording exactly which
piece was missing, because it's a small one.

What I got on my own:
1. **Put everything in a set.** "Is `num + 1` present?" is an exact-match question, so it's
   a hash lookup. Sorting would answer it too, but that's `O(n log n)` and the constraints
   want better.
2. **Check `num - 1`.** I found the right test by myself.

What I got wrong: I was going to use `num - 1 in numSet` as a **counter condition** — walk
the numbers and increment a counter every time a predecessor exists. That doesn't work, and
the reason is worth writing down (see the Explanation). The fix isn't a new test, it's a new
*meaning* for the test I already had:

> `num - 1 not in numSet` doesn't mean "add one". It means **"I am the first number of a
> run."** Only the first number does any work.

Once a number knows it's a head, it just walks forward — `num+1`, `num+2`, … — until the
set runs out. That walk measures its own run, and every run gets measured exactly once by
its own head.

## Complexity

**Time:** `O(n)`  
**Space:** `O(n)`

## Explanation

### Why the counter idea fails

The plan was: one pass, and every time `num - 1` is in the set, bump a counter. Try it on

```
nums = [1, 2, 3, 10, 11, 12]
```

Numbers that have a predecessor: `2, 3, 11, 12` → counter = 4. The answer is **3**.

The counter is measuring the wrong thing. "Has a predecessor" is true of every number that
isn't a head, across the *whole input* — so a single counter adds up the tails of **every
run at once** and gives you `n − (number of runs)`. There's no way to fix it by adjusting
the increment, because a single counter can't tell which run it's counting: you're visiting
the set in arbitrary order, so `11` might come right after `2`.

**A per-sequence answer needs per-sequence bookkeeping.** The counter has to belong to a
run, which means something has to *own* the run. That owner is the head.

### The reframe that fixes it

Same test, different job:

| | your version | the fix |
|---|---|---|
| `num - 1 not in numSet` | (unused) | **"I'm a head — start measuring"** |
| `num - 1 in numSet` | `counter += 1` | **"someone else owns me — do nothing"** |

Every consecutive run has exactly **one** number with no predecessor. Make that number
responsible for measuring the whole run and every run gets measured exactly once, with a
`length` counter that lives inside that one iteration and can't be polluted by other runs.

```
{1, 2, 3, 10, 11, 12}

num = 1   0 not in set  → head. walk 2,3 → length 3   ← longest
num = 2   1 in set      → skip
num = 3   2 in set      → skip
num = 10  9 not in set  → head. walk 11,12 → length 3
num = 11  10 in set     → skip
num = 12  11 in set     → skip
```

### Why this is `O(n)` even though a loop is nested inside a loop

This is the part that looks wrong and isn't, and it's worth knowing cold.

**Nested loops are not automatically `O(n²)`. Count the total work, not the nesting.**

The inner `while` only runs for heads, and a head walks the length of *its own* run. The runs
are disjoint — they don't share a single number — so all the inner walks added together
visit each number **at most once**:

```
total inner steps = length of run 1 + length of run 2 + ... = n
```

The outer loop is `n` iterations, the inner work is `n` in total across all of them, so it's
`O(n)` overall. That's an **aggregate** (amortised) argument, and it's exactly what the
`num - 1` guard buys you. Delete the guard and every number walks its whole run — worst case
`[1..n]` becomes `n + (n-1) + ... = O(n²)`.

### Small things

- Iterate `numSet`, not `nums` — duplicates in the input would each re-do the same walk.
- `length` starts at `1`: the head counts itself.
- Empty input returns `0` because `longest` starts at `0` and the loop never runs.

## Mistakes / what to remember

- **I had the right test and the wrong job for it.** `num - 1 not in numSet` isn't a counter
  condition, it's a **"start of run" detector**. When a check feels right but the counting
  doesn't work, ask what the check should *authorise* rather than what it should *add*.
- **A per-group answer needs a per-group owner.** One global counter can never separate
  groups you visit in arbitrary order. Pick a canonical member of each group (here: the one
  with no predecessor) and make it do the work.
- **Nested loops ≠ `O(n²)`. Count total work.** The inner walks are over disjoint runs, so
  they sum to `n`. Without the head guard it really would be `O(n²)`.
- "Is X present?" is a hash-set question. Sorting also answers it but costs `O(n log n)` —
  check the constraints before paying that.
- `set(nums)` builds the set in one line.

## Solution

See [`solution.py`](./solution.py).
