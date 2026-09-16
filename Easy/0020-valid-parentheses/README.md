# 20. Valid Parentheses

[Problem on LeetCode](https://leetcode.com/problems/valid-parentheses/)

| | |
|---|---|
| **Difficulty** | 🟢 Easy |
| **Topics** | `String`, `Stack`, `Bracket Sequences` |
| **Time to solve** | — |
| **Attempts** | 1 |
| **Solved** | 2026-09-15 |
| **Unaided** | yes |

## My approach

Knew it was a stack instantly — but from repetition, not reasoning. The reasoning I should be
able to produce, written out in the Explanation, is:

> When I see `(` I **cannot decide anything yet**. It's an obligation I have to carry until
> its partner shows up. And when a `)` arrives, the bracket it closes is always the **most
> recent** unclosed one. *Defer, and resolve most-recent-first* — that is the definition of a
> stack.

Map each closer to its opener, push openers, and on a closer check that the top matches.

## Complexity

**Time:** `O(n)`  
**Space:** `O(n)` — worst case `"((((("`

## Explanation

### The three checks, and why each one is needed

```python
if not stack or stack.pop() != brackets[char]:
```

- **`not stack`** — a closer with nothing open. `")("` fails here. Forget it and you get an
  `IndexError` on `pop()` from an empty list.
- **`stack.pop() != brackets[char]`** — a closer that doesn't match what's open. `"(]"`.
- **`len(stack) != 0` at the end** — openers that were never closed. `"((("`.

Three different failure modes, three different tests. Dropping any one of them passes a
suite that doesn't cover it — worth knowing *which* case each line is defending.

### Two cleanups

```python
return not stack          # instead of the if/return False/return True
```

And `char in brackets.values()` rebuilds a view and scans it every character. Cleaner to test
membership in the keys, which is what the dict is for:

```python
for char in s:
    if char in brackets:                       # it's a closer
        if not stack or stack.pop() != brackets[char]:
            return False
    else:                                      # it's an opener
        stack.append(char)
return not stack
```

That version also fails *safe* on unexpected input: a stray letter gets pushed rather than
raising `KeyError` on `brackets[char]`. The constraints promise only brackets, so both work —
but "which branch does a character I didn't anticipate fall into?" is a good habit.

## Mistakes / what to remember

- **The stack tell:** *I can't resolve this now, and when it does resolve it'll be the most
  recent one outstanding.* Nesting is the visible symptom; deferred-work-resolved-newest-first
  is the cause.
- Three separate checks, three separate bugs: **empty stack** on a closer (`")("`),
  **mismatch** (`"(]"`), **leftovers** at the end (`"((("`).
- `return not stack` beats `if len(stack) != 0: return False`.
- Branch on `char in brackets` (the closers) so an unexpected character falls into the
  harmless branch instead of raising `KeyError`.

## Solution

See [`solution.py`](./solution.py).
