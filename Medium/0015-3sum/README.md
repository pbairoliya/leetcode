# 15. 3Sum

[Problem on LeetCode](https://leetcode.com/problems/3sum/)

| | |
|---|---|
| **Difficulty** | 🟡 Medium |
| **Topics** | `Array`, `Two Pointers`, `Sorting` |
| **Time to solve** | — |
| **Attempts** | 1 |
| **Solved** | 2026-09-13 |
| **Unaided** | no |

## My approach

**Reduce it to a problem I've already solved.** Fix one number, and "find three that sum to
0" becomes "find two that sum to `-nums[i]`" — which is
[[0167 Two Sum II - Input Array Is Sorted]] exactly. Sort first so the inner search can be
converging pointers instead of a hash map.

```
for each i:                       ← O(n)
    two-pointer scan of i+1..end  ← O(n)
                                  ⇒ O(n²) total
```

`O(n²)` on `n ≤ 3000` is ~9M operations, comfortably inside budget — the constraints are
telling me `O(n²)` is the target, and `O(n³)` (all triples) is not.

**Where I actually got stuck: duplicates.** Needed hints to see that "no duplicate triplets"
is handled by *skipping equal neighbours*, not by checking the output. Written up properly
below, because that idea is the whole problem.

## Complexity

**Time:** `O(n²)` — `O(n log n)` sort, then `n` two-pointer scans of `O(n)`  
**Space:** `O(1)` excluding the output (the sort is in place)

## Explanation

### The duplicate rule — the thing I had to look up

The insight is one sentence:

> **Sorting turns "is this a duplicate?" from a global membership question into a local
> neighbour comparison.**

Unsorted, "have I already produced this triplet?" means searching everything you've emitted —
`O(n)` per check, and it drags the whole solution back toward `O(n³)`. Sorted, equal values
sit next to each other, so the same question is `nums[x] == nums[x-1]` — one comparison,
`O(1)`, no bookkeeping.

Then the rule is **"only the first occurrence of a value does any work"**, applied at each of
the three positions:

**1. The outer value `i`.**
```python
if i > 0 and nums[i] == nums[i-1]:
    continue
```
The first `-1` in the array already ran a complete two-pointer scan over everything to its
right. A second `-1` scans a *subset* of that same range, so it can only re-find triplets the
first one already emitted. Skip it.

The `i > 0` guard is not decoration: without it `nums[-1]` wraps to the last element and the
first element gets skipped whenever the array's max equals its min.

**2. The left value, after a hit.**
```python
left += 1
right -= 1
while nums[left] == nums[left-1] and left < right:
    left += 1
```
You just emitted a triplet using `nums[left]`. Any other index holding that same value would
produce the identical triplet, so walk past them all.

**3. The right value — already handled, for free.**
Once `i` and `left` are fixed, the third number is *determined*: it must be
`-(nums[i] + nums[left])`. There is only one value that can complete the triplet, so
deduping `i` and `left` is sufficient. This is why solutions that skip only on the left are
correct, and it's worth knowing so you don't add a redundant right-skip and wonder if you
need it.

### Three things to tighten

**1. `[i,left,right] not in sol` is dead code — delete it.**
`sol` holds *values* (`[nums[i], nums[left], nums[right]]`), never index triples, so this
compares indices against values. It can never match: `i < left < right` means
`i + left + right ≥ 0 + 1 + 2 = 3`, while every stored triplet sums to `0`. So the condition
is always `True`.

That's lucky rather than harmless. It reveals the instinct to *dedup by checking the output*,
which is the thing to unlearn: it's an `O(n)` scan inside the hot loop, and the skip-rules
above make it unnecessary. **If your dedup needs to look at the answers you've already
produced, you're deduping at the wrong layer.**

**2. Order the guard before the index.**
```python
while nums[left] == nums[left-1] and left < right:   # reads nums[left] first
while left < right and nums[left] == nums[left-1]:   # bounds first
```
Both survive here (the increment only runs when `left < right`, so `left` can't pass the end),
but the second is the version that's correct by construction. **Bounds check first, then
dereference** — same habit as the guards in [[0125 Valid Palindrome]].

**3. `elif`, and hoist the sum.** Same note as
[[0167 Two Sum II - Input Array Is Sorted]]: three sequential `if`s recompute a sum you just
invalidated by moving a pointer, up to three additions per iteration. It's safe — each move
is independently justified by the discard argument — but the structure should carry the
invariant, not a proof:

```python
while left < right:
    total = nums[i] + nums[left] + nums[right]
    if total > 0:
        right -= 1
    elif total < 0:
        left += 1
    else:
        sol.append([nums[i], nums[left], nums[right]])
        left += 1
        while left < right and nums[left] == nums[left-1]:
            left += 1
```

Note this version doesn't need `right -= 1` on a hit — moving `left` past its duplicates
already guarantees a different pair, and the next comparison repositions `right`.

**Free early exit:** after sorting, `if nums[i] > 0: break`. Once the smallest of the three is
positive, no triplet can reach 0.

## Mistakes / what to remember

- **Reduce k-sum to (k−1)-sum by fixing one element.** 3Sum = a loop around
  [[0167 Two Sum II - Input Array Is Sorted]]. 4Sum = two loops around it. Each fixed element
  costs one factor of `n`.
- **Sorting turns duplicate-detection into a neighbour comparison.** Equal values become
  adjacent, so `nums[x] == nums[x-1]` replaces searching the output. This is *the* lesson of
  this problem.
- **Only the first occurrence of a value does work** — at the outer index (`i > 0 and
  nums[i] == nums[i-1]` → `continue`) and at `left` after a hit. `right` needs no skip,
  because fixing `i` and `left` determines the third value uniquely.
- **Never dedup by scanning the output you've already built.** It's `O(n)` in the hot loop
  and it means you're deduping at the wrong layer.
- **Bounds check before dereference:** `left < right and nums[left] == ...`, not the reverse.
- Don't forget `i > 0` in the outer skip — `nums[-1]` wraps silently.
- `if nums[i] > 0: break` after sorting is a free early exit.

## Solution

See [`solution.py`](./solution.py).
