# 143. Reorder List

[Problem on LeetCode](https://leetcode.com/problems/reorder-list/)

| | |
|---|---|
| **Difficulty** | 🟡 Medium |
| **Topics** | `Linked List`, `Two Pointers`, `Stack`, `Recursion` |
| **Time to solve** | 20m |
| **Attempts** | 1 |
| **Solved** | 2026-09-12 |
| **Unaided** | no |

## My approach

**This one took 20 minutes and I didn't get there on my own. Read the intuition below
before the code.**

The target order is `[0, n-1, 1, n-2, 2, n-3, ...]` — alternate one from the **front**, one
from the **back**. If this were an array it's a five-line problem: a pointer at each end,
walk them toward each other. The whole difficulty is that a *singly* linked list has no way
to walk backwards. There is no `prev`, so the "back pointer" I want simply cannot exist.

So the real question isn't "how do I reorder this" — it's **"how do I get a backwards
iterator out of a singly linked list?"** Two answers:

1. Dump the nodes into an array, then index from both ends. `O(n)` extra space.
2. **Reverse the second half.** Walking the reversed half forwards *is* walking the
   original backwards. `O(1)` extra space.

Once I saw (2), the problem stopped being one problem and became three I already knew:

| step | how | seen before in |
|---|---|---|
| find the middle | fast & slow pointers | — |
| reverse the back half | save / flip / advance | [[0206 Reverse Linked List]] |
| weave the two halves | alternate, splice | [[0021 Merge Two Sorted Lists]] |

That decomposition is the lesson. A hard linked-list problem is usually a *composition* of
easy ones, and the hard part is naming which three.

## Complexity

**Time:** `O(n)`  
**Space:** `O(1)`

## Explanation

Three phases, each one linear, no extra storage.

### 1. Find the middle

```
slow = head
fast = head.next
```

`fast` moves two steps for every one of `slow`'s, so when `fast` falls off the end, `slow`
has covered half the distance. The `head.next` start is deliberate and it is the detail that
makes the rest work:

```
n = 4   2 -> 4 -> 6 -> 8          slow lands on 4   halves: [2,4] [6,8]
n = 5   2 -> 4 -> 6 -> 8 -> 10    slow lands on 6   halves: [2,4,6] [8,10]
```

Starting `fast` at `head.next` puts `slow` on the **last node of the first half**, so the
first half is always equal in length or exactly one longer. Start `fast` at `head` instead
and on even lengths `slow` lands one node further right — the back half ends up longer, and
the merge loop below runs off the end. Which middle you want is a real decision, not a
detail to copy.

### 2. Cut, then reverse

```python
second = slow.next
slow.next = None      # <- the line that everyone forgets
```

**This is where this problem eats people.** Without the cut, the first half still points
into the second half, and after reversing, the second half points back at the first — you
have built a cycle, and the merge loop spins forever. The list has to genuinely become two
separate lists before you touch anything else.

The reversal itself is [[0206 Reverse Linked List]] verbatim: save the rest, flip the arrow,
advance both pointers.

```
after step 2:   first:  2 -> 4 -> None
                second: 8 -> 6 -> None      (was 6 -> 8)
```

### 3. Weave

```python
nextOne, nextTwo = first.next, second.next   # save both futures FIRST
first.next  = second                         # then it is safe to overwrite
second.next = nextOne
first, second = nextOne, nextTwo
```

Same discipline as reversing — **stash before you overwrite**, except here two pointers are
about to be clobbered, so both get saved on the same line before either assignment.

`while second` is the right loop condition precisely because of the choice in step 1: the
back half is never longer, so it runs out first, and whatever is left of the front half is
already attached in the right place. Nothing needs patching up afterwards.

```
2 -> 4        8 -> 6
2 -> 8 -> 4        6        first=4, second=6
2 -> 8 -> 4 -> 6 -> None    second=None, done
```

The function returns `None` and mutates in place, which is what the signature asks for.

## Mistakes / what to remember

- **The real question was "how do I iterate backwards in a singly linked list?"** Answer:
  reverse the part you need to walk backwards. Reversal is a backwards iterator you can
  afford at `O(1)` space.
- **`slow.next = None` is not optional.** Skip the cut and the two halves stay joined;
  after the reverse that's a cycle and the merge never terminates. When a linked-list
  solution hangs, look for a missing cut.
- **`fast = head.next` vs `fast = head` changes which node is "the middle".** Starting at
  `head.next` leaves the first half equal or one longer, which is what lets the merge stop
  cleanly on `while second`. Decide which half should be longer, then pick the start.
- **Save both `next` pointers before reassigning either.** In the weave, two links die per
  iteration, so both futures get stashed on one line first.
- Hard linked-list problems are usually two or three easy ones stacked. Try to name the
  sub-problems before writing anything.
- `head = None` would crash on `head.next`; LeetCode guarantees at least one node, but a
  real implementation would guard it.

## Solution

See [`solution.py`](./solution.py).
