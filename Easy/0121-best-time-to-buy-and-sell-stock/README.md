# 121. Best Time to Buy and Sell Stock

[Problem on LeetCode](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/)

| | |
|---|---|
| **Difficulty** | 🟢 Easy |
| **Topics** | `Array`, `Dynamic Programming` |
| **Time to solve** | 18m |
| **Attempts** | 1 |
| **Solved** | 2026-09-03 |

## My approach

Brute force is every pair of days, O(n^2). But you only ever sell *after* you
buy, so a single left-to-right pass is enough.

## Complexity

**Time:** `O(n)`  
**Space:** `O(1)`

## Explanation

Track the cheapest price seen so far. At each day the best profit ending today
is `price - cheapest`, so keep a running max of that. One pass, no extra space.

## Solution

See [`solution.py`](./solution.py).
