# 206. Reverse Linked List

[Problem on LeetCode](https://leetcode.com/problems/reverse-linked-list/)

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


Can be done recursively or iteratively. Went iterative: walk the list once and
flip each `next` pointer to face backwards.

The intuition is that reversing isn't about moving *nodes*, it's about re-aiming
*arrows*. Each node only needs to know one thing: who came before it. So I carry a
`reverse` pointer holding "everything I've already flipped" and hand each new node
off to it. Naming it `reverse` instead of `prev` makes that read right — it's the
reversed list so far, growing by one node per iteration.

Traced on `1 -> 2 -> 3`:

```
reverse = None            curr -> 1 -> 2 -> 3

step 1:  stash next = 2,  1.next = None       reverse = 1              curr = 2
step 2:  stash next = 3,  2.next = 1          reverse = 2 -> 1         curr = 3
step 3:  stash next = None, 3.next = 2        reverse = 3 -> 2 -> 1    curr = None

loop ends, return reverse
```

Each iteration the list is split in two: `reverse` is the finished (backwards) half,
`curr` is the untouched (forwards) half, and `nextNode` is the one node in flight
between them. That invariant is the whole algorithm.

## Complexity

**Time:** `O(n)`  
**Space:** `O(1)`

## Explanation

Three pointers, one pass. `reverse` is the part of the list already flipped, `curr` is
the node being flipped right now, and `nextNode` saves the rest of the list before
`curr.next` gets overwritten — without that stash the forward half is orphaned and
unreachable the instant you reassign the pointer.

The order inside the loop is forced: **save**, **flip**, **advance** (`reverse` first,
then `curr`). Swap any two of those and you either lose the tail or stop moving.

When `curr` runs off the end, the entire list has been flipped into `reverse`, so
`reverse` is the new head — returning `curr` (which is `None`) or `head` (now the tail)
are the two classic wrong answers here.

## Mistakes / what to remember

- With linked lists, work out which extra pointers you need before writing code.
- When swapping, always keep a temp for the node you're about to orphan.
- Even when `curr.next` is saved in a temp you still have to advance with
  `curr = nextNode` — forgetting that is an infinite loop.
- Return the *new* head (`reverse`), not `head` — after the loop `head` is the tail.

## Solution

See [`solution.py`](./solution.py).
