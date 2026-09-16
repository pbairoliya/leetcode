# 150. Evaluate Reverse Polish Notation

[Problem on LeetCode](https://leetcode.com/problems/evaluate-reverse-polish-notation/)

| | |
|---|---|
| **Difficulty** | 🟡 Medium |
| **Topics** | `Array`, `Math`, `Stack` |
| **Time to solve** | — |
| **Attempts** | 1 |
| **Solved** | 2026-09-15 |
| **Unaided** | yes |

## My approach

Same tell as [[0020 Valid Parentheses]], and in fact **RPN was invented so that a stack could
evaluate it**: operands are written before the operator that consumes them, which removes the
need for precedence rules or parentheses entirely.

> A number is an obligation I can't discharge yet — I don't know what will be done to it. So
> park it. When an operator arrives, the two values it wants are always the **two most
> recently parked**.

Push numbers, and on an operator pop two, combine, push the result back. One pass.

## Complexity

**Time:** `O(n)`  
**Space:** `O(n)`

## Explanation

### `val2` popped first — and why that order matters

```python
val2 = calculate.pop()     # the RIGHT operand comes off first
val1 = calculate.pop()
```

The stack gives them back in reverse, so the **second** pop is the left operand. Irrelevant
for `+` and `*`, fatal for `-` and `/`. Getting this backwards is the single most common bug
in this problem and you avoided it.

### `int(val1/val2)` is correct — and `//` would be wrong

The problem says division **truncates toward zero**. Python's `//` **floors** (rounds toward
negative infinity), and the two disagree on every negative result:

```
int(-7/2) = -3      -7//2 = -4
int(7/-2) = -3      7//-2 = -4
```

So `int(a/b)` is the right call here. Worth knowing the caveat for a stricter setting: it
routes through float division, which starts losing precision past 2^53. The integer-only
truncating idiom is

```python
q = abs(val1) // abs(val2)
newNum = -q if (val1 < 0) != (val2 < 0) else q
```

LeetCode's constraints keep everything well inside float range, so `int(a/b)` is fine — just
know *why* it's fine rather than assuming `//` would have been.

### A cleaner dispatch

The `if/elif` chain is fine and readable. The table version removes the `newNum = 0` dance:

```python
import operator

OPS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": lambda a, b: int(a / b),
}

class Solution:
    def evalRPN(self, tokens: List[str]) -> int:
        stack = []
        for token in tokens:
            if token in OPS:
                b = stack.pop()
                a = stack.pop()
                stack.append(OPS[token](a, b))
            else:
                stack.append(int(token))
        return stack.pop()
```

**Replacing a chain of `if`s over a fixed set of keys with a dict lookup** is a generally
useful move — it's the same instinct as reaching for a hash map in the first place.

### Why RPN needs no parentheses

Infix `3 + 4 * 2` is ambiguous without precedence rules. Postfix `3 4 2 * +` isn't: the
position of each operator already encodes what it applies to. That's the point of the
notation, and it's why the evaluator is ten lines with no parsing.

## Mistakes / what to remember

- **Pop order is reversed: the first pop is the *right* operand.** Doesn't matter for `+`/`*`,
  breaks `-` and `/`. Name them `b, a = pop(), pop()` so the order is visible.
- **`int(a/b)` truncates toward zero; `a//b` floors.** They differ on every negative result
  (`int(-7/2) = -3` vs `-7//2 = -4`). RPN wants truncation. Know which one a problem asks for.
  (`int(a/b)` goes through floats — fine under LeetCode's limits, not for huge integers.)
- **A dict of operators beats an `if/elif` chain** over a fixed key set — same instinct as
  using a hash map instead of a search.
- RPN exists *because* a stack evaluates it in one pass; the notation encodes precedence by
  position, so there's nothing to parse.

## Solution

See [`solution.py`](./solution.py).
