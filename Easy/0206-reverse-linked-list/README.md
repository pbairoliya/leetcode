# 206. Reverse Linked List

[Problem on LeetCode](https://leetcode.com/problems/reverse-linked-list/)

| | |
|---|---|
| **Difficulty** | 🟢 Easy |
| **Topics** | `Linked List`, `Recursion` |
| **Time to solve** | — |
| **Attempts** | 1 |
| **Solved** | 2026-09-02 |

## My approach

Can be done recursively or iteratively. Went iterative: walk the list once and
flip each `next` pointer to face backwards.

## Complexity

**Time:** `O(n)`  
**Space:** `O(1)`

## Explanation

Keep two pointers, `prev` and `curr`. On each step stash `curr.next` in a temp
(`nextNode`) *before* overwriting it, point `curr.next` back at `prev`, then slide
both pointers forward. When `curr` falls off the end, `prev` is the new head.

## Mistakes / what to remember

- With linked lists, work out which extra pointers you need before writing code.
- When swapping, always keep a temp for the node you're about to orphan.
- Even when `curr.next` is saved in a temp you still have to advance with
  `curr = nextNode` — forgetting that is an infinite loop.

## Solution

See [`solution.py`](./solution.py).
