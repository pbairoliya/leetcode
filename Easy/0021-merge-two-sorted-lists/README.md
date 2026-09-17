# 21. Merge Two Sorted Lists

[Problem on LeetCode](https://leetcode.com/problems/merge-two-sorted-lists/)

| | |
|---|---|
| **Difficulty** | 🟢 Easy |
| **Topics** | `Linked List`, `Recursion` |
| **Time to solve** | — |
| **Attempts** | 2 |
| **Solved** | 2026-09-02 |
| **Unaided** | yes |

## My approach

> [!success] Rewritten from blank on review, 2026-09-16 — unaided.


The inputs are **already sorted**, so there's nothing to sort — just splice. At every step
only the two *heads* can be the next smallest, so one comparison per node is enough.

The dummy head (`ListNode(-1)`) is what removes the "is this the first node?" special case;
return `newHead.next`, never `newHead`.


Both inputs are already sorted, so nothing needs sorting — weave them together
in one pass, always taking the smaller of the two heads.

## Complexity

**Time:** `O(n + m)`  
**Space:** `O(1)`

## Explanation

### Two lines the dummy already handles

```python
if not list1 and not list2:
    return list1
```

Unnecessary. With both lists empty the `while` never runs, both tail checks fail, and
`newHead.next` is already `None`. **That's the whole point of the dummy** — it makes the empty
case indistinguishable from every other case. Deleting the guard is a small test of whether
you trust the sentinel.

Same for the tail:

```python
if list1:
    newCurr.next = list1
elif list2:
    newCurr.next = list2
```

Exactly one of them is non-empty when the loop exits (the loop only ends when one runs out),
so this is just:

```python
newCurr.next = list1 or list2
```

### Why `<=` and not `<`

With equal values, taking from `list1` first keeps the merge **stable** — equal elements come
out in their original relative order. It doesn't change correctness here (the values are
identical), but stability is a real requirement in the general merge, and `<=` is the habit to
build.


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
