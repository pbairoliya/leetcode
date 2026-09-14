# 167. Two Sum II - Input Array Is Sorted

[Problem on LeetCode](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/)

| | |
|---|---|
| **Difficulty** | 🟡 Medium |
| **Topics** | `Array`, `Two Pointers`, `Binary Search` |
| **Time to solve** | — |
| **Attempts** | 1 |
| **Solved** | 2026-09-13 |

## My approach

Straight to converging pointers ([[0125 Valid Palindrome]] §5.6) — the tells are stacked:
**sorted input** and **"must use `O(1)` additional space"**. That second line is the problem
telling me not to use a hash map.

Worth holding next to [[0001 Two Sum]], because it's the same question with one changed
premise and a completely different answer:

| | [[0001 Two Sum]] | this one |
|---|---|---|
| input | unsorted | **sorted** |
| tool | hash map | **converging pointers** |
| time | `O(n)` | `O(n)` |
| space | `O(n)` | **`O(1)`** |

Sortedness is what you're paying for: it means the comparison tells you *which* pointer to
move. Without order, knowing a sum is too big tells you nothing about where to look next.

## Complexity

**Time:** `O(n)`  
**Space:** `O(1)`

## Explanation

### Why moving the "wrong" pointer never loses the answer

This is the question worth being able to answer out loud, because it's the whole justification
for the pattern.

Suppose `numbers[left] + numbers[right] > target`. Ask: **could `numbers[right]` be part of
the answer?** Its best possible partner is the *smallest* number still available — which is
`numbers[left]`, because the array is sorted and everything left of `left` is already
discarded. Even that best case overshoots. So `numbers[right]` cannot pair with anything
remaining, and discarding it throws away nothing.

The mirror argument covers `< target`: `numbers[left]`'s best partner is the largest one
left, `numbers[right]`, and even that undershoots — so `left` is dead.

Each step eliminates exactly one candidate and never eliminates the answer, so after at most
`n` steps the pointers have either found the pair or proven there isn't one. It's the same
shape as binary search: **every comparison kills half the remaining possibilities** — here,
one row or one column of the implicit `n × n` grid of pairs.

### Why your three `if`s are still correct

After `right -= 1`, the second `if` re-evaluates with the new pair, so a single iteration can
move `right` *and then* `left`. That's not a bug, because each move is independently
justified by the argument above — the second discard is just as valid with the new `right` as
it would have been at the top of the next iteration.

It also can't return a bad pair. The only worrying case is the pointers crossing mid-iteration
(`left` ending up past `right`), which needs `right - left == 1` at the top, `sum > target`,
then `2 × numbers[left] < target`. But the first condition says
`numbers[left] + numbers[left+1] > target`, so the crossed pair can never *also* equal the
target. And indices stay in range: `right` never drops below `left`'s old value, `left` never
climbs past `right + 1`.

So: correct, but it costs up to three additions per iteration and rests on a proof instead of
on structure. The `elif` version is the one to write.

### Two small things

- **The sum is recomputed up to three times.** `s = numbers[left] + numbers[right]` once at
  the top of the loop reads better and is what the `elif` version wants anyway.
- **`return [-1, -1]` is unreachable** — the problem guarantees exactly one solution. Keeping
  it is fine and defensive; just know it's not load-bearing, and don't let an unreachable
  fallback convince you the loop handles a case it doesn't.
- **1-indexed output** (`left + 1`, `right + 1`). You got it; it's the most common careless
  loss on this problem.

## Mistakes / what to remember

- **Sorted + "`O(1)` space" is the two-pointer signal**, stated almost explicitly in the
  constraints. When a problem names a space bound, it's naming the technique.
- **The discard argument is the pattern**, not the code: *if the sum is too big, the right
  element's best possible partner already overshoots, so it can't be in any answer.* Be able
  to say that sentence — it's the "why" for every converging-pointer problem.
- **Use `if / elif / else`, not three `if`s.** Sequential `if`s re-test state you just
  mutated. Safe here, but the structure should carry the invariant "one pointer moves per
  iteration" instead of a proof carrying it.
- Compute the sum once into a variable rather than three times.
- Same problem as [[0001 Two Sum]] with one premise changed: unsorted → hash map `O(n)`
  space; sorted → pointers `O(1)` space.
- Watch the 1-indexed return.

## Solution

See [`solution.py`](./solution.py).
