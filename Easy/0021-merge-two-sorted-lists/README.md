# 21. Merge Two Sorted Lists

[Problem on LeetCode](https://leetcode.com/problems/merge-two-sorted-lists/)

| | |
|---|---|
| **Difficulty** | 🟢 Easy |
| **Topics** | `Linked List`, `Recursion` |
| **Time to solve** | — |
| **Attempts** | 1 |
| **Solved** | 2026-09-02 |

## My approach

Both inputs are already sorted, so nothing needs sorting — weave them together
in one pass, always taking the smaller of the two heads.

## Complexity

**Time:** `O(n + m)`  
**Space:** `O(1)`

## Explanation

Use a dummy head so there's no special case for the first append. Walk both
lists while neither is exhausted, appending whichever head is smaller and
advancing that list. When one runs out the other is already sorted, so append it
wholesale. Return `dummy.next`.

## Mistakes / what to remember

- The inputs being pre-sorted is the whole trick — no sorting, just piece the
  two lists together.
- The dummy head is what removes the "is this the first node?" branch.

## Solution

See [`solution.py`](./solution.py).
