# 567. Permutation in String

[Problem on LeetCode](https://leetcode.com/problems/permutation-in-string/)

| | |
|---|---|
| **Difficulty** | 🟡 Medium |
| **Topics** | `Hash Table`, `Two Pointers`, `String`, `Sliding Window` |
| **Time to solve** | — |
| **Attempts** | 1 |
| **Solved** | 2026-09-15 |
| **Unaided** | yes |

## My approach

Two observations chained together:

1. **"A permutation of `s1`" = "the same multiset of letters as `s1`."** Order is irrelevant,
   so the thing to compare is a **frequency map**, not the string. Same reframe as any
   anagram problem.
2. **A permutation of `s1` has exactly `len(s1)` characters.** So the window size is known
   before I look at `s2` at all — this is a **fixed** window, not a variable one.

Then it's: slide a frame of width `len(s1)` across `s2`, keep a frequency map of what's
inside the frame, and after each slide ask "does this map equal `s1`'s map?"

## Complexity

**Time:** `O(n × 26)` → `O(n)` — one pass, and each dict comparison is bounded by the alphabet  
**Space:** `O(26)` → `O(1)`

## Explanation

### `del` on a zero count is not optional

```python
s2Freq[s2[left]] -= 1
if s2Freq[s2[left]] == 0:
    del s2Freq[s2[left]]
```

With plain dicts, `{'a': 1, 'b': 0} != {'a': 1}`. Leave the zero entry in and the comparison
fails even when the window is a genuine permutation. Deleting it keeps the map **canonical**:
one dict per multiset, so `==` means what you want it to mean.

> `collections.Counter` is the exception — since Python 3.10 its `__eq__` ignores zero counts,
> so `Counter(s1) == windowCounter` works without the `del`. Nice to know, but don't rely on
> it with plain dicts.

### You don't actually need `left` here

The window only ever overflows by **one** character, so `right - left + 1 > len(s1)` is just a
long way of saying "we're past the first full window", and `left` is always `right - len(s1) + 1`.
The fixed-window idiom drops the variable entirely:

```python
k = len(s1)
for right in range(len(s2)):
    add(s2[right])
    if right >= k:
        remove(s2[right - k])      # the character that fell off the back
    if right >= k - 1 and s1Freq == s2Freq:
        return True
```

**No `left`, no inner `while`.** That's the shape of every fixed window — and noticing that
your `left` is a derived quantity rather than a real variable is a good sign you've correctly
identified the problem as fixed.

### Making it truly `O(n)`

`s1Freq == s2Freq` walks up to 26 keys on every step. To get the comparison to `O(1)`, track
a `matches` counter — how many of the 26 letters currently have equal counts — and update it
only for the two letters that changed per slide. Worth knowing for the follow-up question;
`O(26n)` passes fine here.

### Fixed vs variable — how to tell

> **Can you compute the window's size before looking at the data? Then it's fixed.**

| | fixed | variable |
|---|---|---|
| where the size comes from | the **problem** gives it — `k`, or `len(s1)`, or `len(p)` | the **condition** decides it |
| phrasing | "subarray of size `k`", "permutation/anagram of `s1`", "average of every `k`" | "longest … such that", "shortest … such that", "at most `k` distinct" |
| left edge | moves in lockstep, one per step — often not a variable at all | moves an unpredictable amount |
| inner loop | **none** | a `while` that repairs or shrinks |
| when you check | once per position, after the frame is full | after repairing (longest) or while shrinking (shortest) |

The tell in this problem is subtle because the size is **implied** rather than stated: nothing
says "window of size 5", but "a permutation of `s1`" forces `len(s1)`. **Anything that fixes
the *content* fixes the size.**

Both templates are in §5.6 of [[Leetcode Study Guide]].

## Mistakes / what to remember

- **Fixed vs variable, the one-line test:** *can I compute the window size before looking at
  the data?* Yes → fixed (no inner `while`, no real `left`). No → variable (inner `while`,
  `left` moves unpredictably).
- **The size can be implied.** "A permutation/anagram of `s1`" never says a number, but it
  pins the width to `len(s1)`. Anything that fixes the content fixes the size.
- **"Permutation of" / "anagram of" means compare frequency maps, not strings.** Order is
  exactly what you're allowed to ignore.
- **Delete zero-count keys** so the dict stays canonical — `{'a':1,'b':0} != {'a':1}` for
  plain dicts. (`Counter` ignores zeros since Python 3.10.)
- **In a fixed window, `left` is derived, not tracked:** `left == right - k + 1`. If you're
  maintaining it by hand, you can usually delete it.
- The `O(1)`-comparison upgrade is a `matches` counter updated only for the two letters that
  changed each slide — the answer to "can you do better than 26 per step?"

## Solution

See [`solution.py`](./solution.py).
