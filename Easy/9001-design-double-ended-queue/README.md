# 9001. Design Double-ended Queue

[Problem on LeetCode](https://neetcode.io/problems/queue)

| | |
|---|---|
| **Difficulty** | 🟢 Easy |
| **Topics** | — |
| **Time to solve** | 8m |
| **Attempts** | 1 |
| **Solved** | 2026-09-12 |

## My approach

The constraint *is* the hint: **`O(1)` at both ends**. That immediately rules out a Python
list — `append`/`pop` are `O(1)` at the right, but `insert(0, x)`/`pop(0)` are `O(n)` because
every other element shifts. So I need a structure where "the ends" are things I can *hold*
rather than *find*.

A **doubly linked list** is exactly that: keep a `head` and a `tail` pointer, and every
operation is a couple of pointer reassignments — no traversal anywhere. `prev` is the part
that makes it double-ended; with only `next` I could pop from the front in `O(1)` but
popping from the back would mean walking the whole list to find the second-to-last node.

I also keep an explicit `size` counter so `isEmpty` is `O(1)` and doesn't depend on
inspecting pointers.

## Complexity

**Time:** `O(1)` per operation  
**Space:** `O(n)` for `n` items

## Explanation

Every operation touches a fixed number of pointers, so nothing scales with `n`.

**Insertion** is the same three moves at either end: point the new node at the old end,
point the old end back at the new node, then move `head`/`tail` onto it. The empty case is
special only because there is no old end to link to — `head` and `tail` both become the one
node.

**Removal** is one move: slide `head` (or `tail`) onto its neighbour. The removed node
becomes unreachable from the outside, so it's gone as far as the caller is concerned.

### Two things worth fixing

**1. Removal leaves dangling pointers.** After `self.tail = self.tail.prev`, the new tail's
`next` still points at the node you just removed, and that removed node's `prev` still points
into the live list:

```
before pop:   A <-> B <-> C          tail = C
after  pop:   A <-> B  ->  C         tail = B     (B.next is still C, C.prev is still B)
```

Nothing in *this* API ever reads `B.next`, so the tests pass. But it means the node can't be
garbage collected while `B` is alive, and the moment you add any method that walks forward
(`__len__`, iteration, `peek`, `__repr__`) it produces a ghost element. Unlinking is one
extra line:

```python
self.tail = self.tail.prev
if self.tail:
    self.tail.next = None
```

**2. The last removal leaves a stale pointer on the other side.** Pop the final element and
`tail` becomes `None` while `head` still points at the removed node — the object is now in
an inconsistent state that only *looks* fine because every method guards on `size` first.
That is accidental correctness, and accidental correctness breaks the day someone writes a
method that trusts `head`. Make emptiness explicit:

```python
self.size -= 1
if self.size == 0:
    self.head = self.tail = None
```

### The trick that deletes all of this: sentinels

Every `if self.isEmpty()` branch above exists to answer "is there a neighbour to link to?"
Allocate two permanent dummy nodes at construction and the answer is always yes:

```python
self.left, self.right = ListNode(0), ListNode(0)   # never hold real data
self.left.next, self.right.prev = self.right, self.left
```

Now the list is always `left <-> ... <-> right`, every real node has a real neighbour on
both sides, and insert/remove become straight-line code with no empty case at all:

```python
def append(self, value):
    node, prev = ListNode(value), self.right.prev
    prev.next = node
    node.prev, node.next = prev, self.right
    self.right.prev = node
    self.size += 1
```

Same `O(1)`, half the branches, and no way to leave a stale `head`. This is the standard
shape for linked-list design problems — it's exactly the structure inside an LRU cache.

## Mistakes / what to remember

- **"`O(1)` at both ends" means doubly linked list.** An array is `O(n)` at the front
  because everything shifts. If the problem says both ends, you need `prev`.
- **Unlink in both directions when you remove.** `self.tail = self.tail.prev` moves the
  handle but leaves `new_tail.next` pointing at a corpse.
- **After removing the last element, reset *both* `head` and `tail` to `None`.** Relying on
  a `size` guard to hide a stale pointer is a bug waiting for the next method you add.
- **Dummy head/tail sentinels delete every empty-list special case.** Reach for them in any
  linked-list design problem — same trick makes an LRU cache clean.
- `isEmpty` is just `return self.size == 0`; the `if/return True/return False` is the long
  way to write a boolean.

## Solution

See [`solution.py`](./solution.py).
