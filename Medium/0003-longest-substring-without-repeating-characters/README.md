# 3. Longest Substring Without Repeating Characters

[Problem on LeetCode](https://leetcode.com/problems/longest-substring-without-repeating-characters/)

| | |
|---|---|
| **Difficulty** | 🟡 Medium |
| **Topics** | `Hash Table`, `String`, `Sliding Window` |
| **Time to solve** | — |
| **Attempts** | 1 |
| **Solved** | 2026-09-15 |

## My approach

Took a while to see it was a sliding window. The recognition procedure I should have run is
written up in the Explanation — it's three questions, and this problem answers all three
loudly.

Brute force: every `(start, end)` pair, check for duplicates — `O(n²)` windows, `O(n)` to
check each. The waste is that extending the end **re-examines the whole window** when almost
all of it is unchanged. So: maintain the window incrementally instead of rebuilding it, and
never let the left edge move backwards.

Wrote two versions — a crawling one and a jumping one. Both `O(n)`, and they differ in a way
worth understanding.

## Complexity

**Time:** `O(n)` — `left` and `right` each move forward at most `n` times  
**Space:** `O(min(n, alphabet))`

## Explanation

### How to recognise a sliding window

Three questions, in order. This problem shouts the answer to all three.

**1. What *shape* is the answer?** Not the algorithm — the answer. A pair? A count? A
**contiguous run**? Here it's "a substring", and *substring means contiguous*. That one word
eliminates most of the decision table. (Contrast **subsequence**, which allows skipping —
that's almost always DP, never a window.)

**2. What is the brute force re-computing?** Every `(start, end)` pair, re-scanning the whole
window each time. But when you slide the end forward by one, the window barely changed. The
waste is *rebuilding state you could have updated*.

**3. Is validity monotone under shrinking?** This is the real test, and the one nobody
articulates:

> **If a window is valid, is every window inside it also valid?**

"No repeated characters" — yes: any substring of a duplicate-free string is duplicate-free.
That's what makes shrinking from the left safe. When adding `s[right]` breaks the window, you
know the fix is to give up some prefix — you never have to restart, and you never have to
move `left` backwards.

**If the answer to 3 is no, it isn't a window.** That's the test that separates this from
problems that look similar and aren't.

So:

| the problem says | → |
|---|---|
| "substring", "subarray", "consecutive" | contiguous ⇒ window is a candidate |
| "longest / shortest / count of" + a condition | window over a predicate |
| the condition survives shrinking | **sliding window**, confirmed |
| "subsequence", reordering allowed | **not** a window — think DP or sorting |

### Why it's `O(n)` with a loop inside a loop

Same aggregate argument as [[0128 Longest Consecutive Sequence]] and
[[0125 Valid Palindrome]]: **`left` only ever increases**. Across the entire run it advances
at most `n` times total, no matter how the inner `while` is distributed. Count total moves,
not loop nesting.

**`left` never moves backwards** is the invariant of every sliding window. Write that sentence
before you write the loop.

### The two templates

```python
# LONGEST valid window: expand, repair, then record
for right in ...:
    add(right)
    while invalid():
        remove(left); left += 1
    best = max(best, right - left + 1)

# SHORTEST valid window: expand, then record while shrinking
for right in ...:
    add(right)
    while valid():
        best = min(best, right - left + 1)
        remove(left); left += 1
```

Longest records *after* repairing; shortest records *while* shrinking. Getting these two
backwards is the most common sliding-window bug. (To **count** windows instead, add
`right - left + 1` — the number of valid windows ending at `right`.)

### Crawl vs jump

Version A moves `left` one step at a time until the duplicate is gone. Version B stores the
**last index of each character** and teleports `left` straight past it.

Both are `O(n)`; B just does the same total work without an inner loop. The subtle part in B
is the `max`:

```python
left = max(left, lastChar[s[right]])
```

**Without that `max`, `left` can move backwards** and the answer inflates. Trace `"abba"`:

```
right=0 'a'  left=-1  lastChar={a:0}        len = 0-(-1) = 1
right=1 'b'  left=-1  lastChar={a:0,b:1}    len = 1-(-1) = 2
right=2 'b'  b seen at 1 → left = max(-1,1) = 1   len = 2-1 = 1
right=3 'a'  a seen at 0 → left = max(1, 0) = 1   len = 3-1 = 2   ← the max saves it
```

At `right=3`, `'a'`'s last index is `0`, which is *behind* the current window. Without the
`max` you'd set `left = 0` and report length `3` for `"bba"`. The `max` enforces the
invariant directly: **left never moves backwards.**

### The `+1`, again

Version A uses `right - left + 1`; version B uses `right - left`. Both are right, because
`left` means different things:

- **A:** `left` is the first index *inside* the window → inclusive `[left, right]` → `+1`.
- **B:** `left` is the last index *outside* the window → exclusive `(left, right]` → no `+1`.
  That's also why it starts at `-1`.

Same distinction as the width in [[0011 Container With Most Water]]: `+1` counts elements in
an inclusive range; a plain difference measures a span. **Decide which one `left` means before
you write the formula**, and the `+1` stops being a guess.

## Mistakes / what to remember

- **The sliding-window tell, in three questions:** is the answer a *contiguous* run? is the
  brute force rebuilding a window it could update? and — **the real test** — *if a window is
  valid, is every window inside it valid too?* If that last one is no, it isn't a window.
- **"Substring"/"subarray" = contiguous = window candidate. "Subsequence" = skipping allowed
  = not a window** (think DP).
- **The invariant of every window is "`left` never moves backwards."** Write that first; it's
  also why `for`+`while` is still `O(n)` — count total moves, not nesting.
- **Longest records *after* repairing; shortest records *while* shrinking.** Mixing up the two
  templates is the classic bug.
- **In the jump version, `left = max(left, lastSeen)` is load-bearing** — a stale index from
  before the window would drag `left` backwards. `"abba"` is the test case that catches it.
- **`+1` or not depends on whether `left` is inside or outside the window.** Inclusive
  `[left, right]` → `right - left + 1`; exclusive `(left, right]` → `right - left`, starting
  at `-1`. Decide the meaning first.
- The `if len(s) <= 1` early return isn't needed — the loop already handles both.

## Solution

See [`solution.py`](./solution.py).
