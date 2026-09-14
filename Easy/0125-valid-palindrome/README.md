# 125. Valid Palindrome

[Problem on LeetCode](https://leetcode.com/problems/valid-palindrome/)

| | |
|---|---|
| **Difficulty** | 🟢 Easy |
| **Topics** | `Two Pointers`, `String` |
| **Time to solve** | — |
| **Attempts** | 1 |
| **Solved** | 2026-09-13 |

## My approach

Easy one — first thing that worked. Worth naming the pattern anyway, because it's a
**fourth** two-pointer configuration and I'll see it constantly:

> **Converging pointers.** One at each end, walking inward. *Invariant: everything outside
> `[left, right]` has already been checked and matched.*

"Palindrome" is a statement about **position** — character `i` from the front must equal
character `i` from the back — not about membership or frequency. A set or a counter can't
express that, but two indices walking toward each other can.

The obvious alternative is to filter into a clean string and compare it to its reverse:

```python
t = [c.lower() for c in s if c.isalnum()]
return t == t[::-1]
```

Three lines, same `O(n)` time — but `O(n)` extra space for the copy. Two pointers do it in
`O(1)`. That's the only real trade here, and it's the reason the interview version asks for
two pointers.

## Complexity

**Time:** `O(n)`  
**Space:** `O(1)`

## Explanation

Three loops, but still one pass: `left` only ever increases and `right` only ever decreases,
so together they cover each index **once**. `O(n)`, not `O(n²)` — the same "count total
touches, not nesting" argument as [[0128 Longest Consecutive Sequence]].

The inner `while`s do the skipping. The guard `left < right` inside them is the part that
matters: without it, a string of pure punctuation (`",,,"`) would run `left` straight past
the end and index out of range. With it, the pointers meet and the outer loop exits.

**Why it's `True` when the pointers meet.** For odd-length palindromes the middle character
is its own mirror, so there's nothing to check. `left < right` (not `<=`) skips it for free.

### Two cleanups

`str.isalnum()` is the built-in for `alphaNum`:

```python
def isPalindrome(self, s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left, right = left + 1, right - 1
    return True
```

One caveat worth knowing: `isalnum()` is **Unicode-aware**, so `'²'` and `'é'` are alnum to
Python but not under this problem's "A-Z, a-z, 0-9" definition. The constraints here promise
printable ASCII, so it's safe — but on a problem that allows Unicode, the explicit `ord()`
version is the correct one, not the naive one.

Also `.lower()` is being called twice per character — once inside `alphaNum`, once in the
comparison. Harmless, but the `alphaNum` copy does nothing for the caller, since lowering
inside a function doesn't change the character outside it.

## Mistakes / what to remember

- **Converging two pointers = positional symmetry.** When the claim is "the `i`-th from the
  front matches the `i`-th from the back" (palindrome, pair summing to a target in a sorted
  array, container with most water), walk inward from both ends. Sets and counters can't
  express position.
- **Keep the `left < right` guard inside the skip loops.** An all-punctuation string walks a
  pointer off the end without it.
- **`left < right`, not `<=`** — the middle character of an odd-length palindrome is its own
  mirror and needs no check.
- Three nested `while`s, still `O(n)`: each pointer only moves one direction, so every index
  is touched once.
- `c.isalnum()` is the built-in — but it's **Unicode-aware**, so it's broader than "A-Z a-z
  0-9". Fine under ASCII constraints, wrong otherwise.
- The filter-and-reverse one-liner (`t == t[::-1]`) is the same `O(n)` time but `O(n)` space.
  Know both; say which you're choosing and why.

## Solution

See [`solution.py`](./solution.py).
