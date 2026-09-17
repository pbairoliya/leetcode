# 128. Longest Consecutive Sequence

[Problem on LeetCode](https://leetcode.com/problems/longest-consecutive-sequence/)

| | |
|---|---|
| **Difficulty** | 🟡 Medium |
| **Topics** | `Array`, `Hash Table`, `Union-Find` |
| **Time to solve** | — |
| **Attempts** | 2 |
| **Solved** | 2026-09-13 |
| **Unaided** | yes |

## My approach

> [!success] Redone from a blank file 2026-09-16 — **unaided, and I found the optimal myself.**
> First attempt was the `O(n·k)` version below; I spotted the waste and fixed it. Recording
> both, because the *difference between them* is the entire problem.

**The reframe:** "is `x` present?" is an exact-match question ⇒ a hash set. Sorting also
answers it but costs `O(n log n)`, and the constraints want better.

**The insight I had to find the first time and produced on my own this time:**

> `num - 1 not in numSet` isn't a counter condition. It means **"I am the first number of a
> run"** — and *only* the first number does any work.

## Complexity

**Time:** `O(n)` optimal · `O(n·k)` for the first attempt, where `k` is the longest run  
**Space:** `O(n)`

## Explanation

### Two changes turn `O(n·k)` into `O(n)`

The first version is *correct*. It's slow for two separate reasons, and it's worth keeping
them apart because only one of them is the real idea.

**1. The head guard — this is the whole optimisation.**
Without `if num - 1 in numSet: continue`, **every** member of a run walks its own suffix. A
run of length `k` costs `k + (k-1) + ... + 1 = O(k²)` instead of `O(k)`. On `[1..n]` that's
the difference between:

```
no head guard on [1..2000]:  1,999,000 inner steps   (~n²/2)
with head guard:                 1,999 inner steps   (= n)
```

A 1000× difference at `n = 2000`, and the constraint is `n = 10^5`. **The guard is what makes
the walks disjoint**, which is what makes the aggregate argument work: each number is stepped
over exactly once across the entire run of the program, so a `while` inside a `for` is still
`O(n)`.

**2. Iterating `nums` instead of `numSet`.**
Duplicates each redo the identical walk. Cheaper to fix and a smaller win, but free.

A third, smaller one: a **set** is the right structure, not a frequency map. You only ever ask
*"is it present?"* — the counts are never read, so building them is wasted work and wasted
space.


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

- **I had the right test and the wrong job for it** (first time round). `num - 1 not in
  numSet` isn't a counter condition, it's a **"start of run" detector**. When a check feels
  right but the counting doesn't work, ask what the check should *authorise*, not what it
  should *add*.
- **A per-group answer needs a per-group owner.** One global counter can never separate groups
  you visit in arbitrary order.
- **The head guard isn't a micro-optimisation — it's the algorithm.** Without it every member
  of a run re-walks the run: `O(k²)` per run. Measured on `[1..2000]`: 1,999,000 inner steps
  without it, 1,999 with. It's what makes the walks *disjoint*, which is what makes the
  nested `while` still `O(n)`.
- **Iterate the set, not the list** — duplicates otherwise redo identical work.
- **Use a `set`, not a frequency map,** when you only ever ask "is it present?". Counts you
  never read are wasted time and space.
- `set(nums)` builds it in one line.
- Minor: the optimal version mutates the loop variable `num` inside the `while`. Safe in
  Python (the iterator is unaffected), but `curr = num` reads better and can't surprise you.

## Solution

See [`solution.py`](./solution.py).
