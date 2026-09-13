# 19. Remove Nth Node From End of List

[Problem on LeetCode](https://leetcode.com/problems/remove-nth-node-from-end-of-list/)

| | |
|---|---|
| **Difficulty** | 🟡 Medium |
| **Topics** | `Linked List`, `Two Pointers` |
| **Time to solve** | — |
| **Attempts** | 1 |
| **Solved** | 2026-09-12 |

## My approach

"nth from the end" is the same shape as [[0143 Reorder List]]: the list only moves forwards,
but the question is asked from the back. Two ways out — count the length first and walk
`len - n` from the front (two passes), or **build a gap**.

The gap idea: put one pointer `n` steps ahead of another, then move both at the same speed.
The distance between them never changes, so at the moment the leader falls off the end, the
follower is sitting exactly `n` from the end. **The gap is the measurement** — I never need
to know the length.

One extra move: to delete a node in a singly linked list I need the node *before* it, so the
follower should trail by `n + 1`, not `n`. Starting the follower at a **dummy node** in
front of `head` does that for free, and it also handles removing the head itself, which is
otherwise a special case (`n == len`).

## Complexity

**Time:** `O(n)` — one pass  
**Space:** `O(1)`

## Explanation

### The invariant

Everything here follows from one sentence: **the distance between two pointers moving at the
same speed never changes.** So set the distance up front, then let the end of the list tell
you when to stop.

```
n = 2,  list = 1 -> 2 -> 3 -> 4

phase 1: push lead n steps ahead
  dummy -> 1 -> 2 -> 3 -> 4 -> None
  ^trail            ^lead                (gap = 3 nodes = n + 1)

phase 2: move both until lead falls off
  dummy -> 1 -> 2 -> 3 -> 4 -> None
           ^trail            ^lead
  dummy -> 1 -> 2 -> 3 -> 4 -> None
                ^trail             ^lead = None

trail is now the node BEFORE the target. trail.next = trail.next.next
  1 -> 2 -> 4
```

### Why `n + 1` and not `n`

A singly linked list can only delete by **skipping**: you reach into the *previous* node and
point its `next` past the victim. So the follower has to stop one node early. Your code gets
this right in a slightly hidden way — `lead` advances `n` steps from `head`, but `trail`
starts at `dummy`, which is one node *behind* `head`. That off-by-one offset is the `+1`.

### Why the dummy is doing real work

Try `[1,2], n = 2` without it. The node to remove is the head, so the "node before it"
doesn't exist, and you'd need a special case: `if trail is None: return head.next`. The dummy
manufactures that missing predecessor, so there is exactly one code path. **Any time a
linked-list operation might touch the head, a dummy node deletes the special case** — the
same trick as the sentinels in [[9001 Design Double-ended Queue]].

Returning `dummy.next` rather than `head` matters for the same reason: if `head` was the node
removed, `head` is now stale.

### The guard in phase 1

`while second and i < n` — the `second and` half is defensive. The constraints promise
`1 <= n <= sz`, so `lead` can never run off early; without that promise, a too-large `n`
would crash on `None.next`. Keeping it costs nothing and is the right instinct.

## Mistakes / what to remember

- **Name pointers for their job: `lead`/`trail`, or `fast`/`slow`.** `first`/`second` that
  mean the opposite of what they say is most of the confusion in this one.
- **The gap *is* the measurement.** Two pointers at the same speed hold their distance, so
  offsetting them by `k` and running to the end locates "`k` from the end" in one pass, with
  no length count.
- **Trail by `n + 1`, not `n`** — deleting in a singly linked list needs the node *before*
  the victim, because you delete by skipping.
- **Reach for a dummy node whenever the head might be removed or replaced.** It invents the
  predecessor that `head` doesn't have and collapses two code paths into one.
- Return `dummy.next`, never `head` — `head` may be the node you just deleted.

## Solution

See [`solution.py`](./solution.py).
