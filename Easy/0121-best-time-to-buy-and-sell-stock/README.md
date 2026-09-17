# 121. Best Time to Buy and Sell Stock

[Problem on LeetCode](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/)

| | |
|---|---|
| **Difficulty** | 🟢 Easy |
| **Topics** | `Array`, `Dynamic Programming` |
| **Time to solve** | 18m |
| **Attempts** | 2 |
| **Solved** | 2026-09-03 |
| **Unaided** | yes |

## My approach

> [!success] Rewritten from blank on review, 2026-09-16 — unaided.


The invariant, said before coding: **`bestBuy` is the cheapest price seen so far, and the best
profit *ending today* is `price - bestBuy`.** One summary number about the past is all this
problem needs, so the `O(n²)` all-pairs loop collapses to one pass.


Brute force is every pair of days, O(n^2). But you only ever sell *after* you
buy, so a single left-to-right pass is enough.

## Complexity

**Time:** `O(n)`  
**Space:** `O(1)`

## Explanation

### Is the order of the two updates load-bearing here?

Worth checking deliberately, because in [[0042 Trapping Rain Water]] the equivalent ordering
**is** load-bearing (refresh the running max *before* you subtract, or you go negative).

Here it isn't. If `bestBuy` were updated first, then on a new minimum you'd compute
`price - price = 0`, which can never lower `profitMax`. Both orders give the same answer —
buying and selling on the same day is legal and worth nothing.

**The habit is to ask, not to assume.** Two problems, the same shape, opposite answers:
the ordering matters in 42 because a bar can be its own wall; it doesn't matter here because
a zero-profit trade is harmless.

The `if price > bestBuy` guard is also optional — without it, `price - bestBuy` is `≤ 0` and
`max` keeps the old value. It does earn its keep in one way: it avoids arithmetic on
`float("inf")` on the first iteration.


Track the cheapest price seen so far. At each day the best profit ending today
is `price - cheapest`, so keep a running max of that. One pass, no extra space.

## Solution

See [`solution.py`](./solution.py).
