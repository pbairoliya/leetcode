# 1. Two Sum

[Problem on LeetCode](https://leetcode.com/problems/two-sum/)

| | |
|---|---|
| **Difficulty** | 🟢 Easy |
| **Topics** | `Array`, `Hash Table` |
| **Time to solve** | 37m |
| **Attempts** | 2 |
| **Solved** | 2026-09-03 |
| **Unaided** | yes |

## My approach

> [!success] Rewritten from blank on review, 2026-09-16 — unaided.


Brute force is the pair-wise double loop, `O(n^2)`. The insight: I never need to *search*
for the complement, I need to *look it up*. A hash map is the right tool whenever the
question is "does this exact value exist, and where?" — that's an `O(1)` lookup instead of
an `O(n)` scan, which is what collapses the nested loop into one pass over the array.

So: map every value to its index, then for each number ask the map for `target - number`.
The only trap is matching an element with itself, hence the `numMap[targetNum] != i` guard.

## Complexity

**Time:** `O(n)`  
**Space:** `O(n)`

## Explanation

> [!tip] Still writing two passes
> Third time through this one and it's still the two-pass version. The one-pass is the same
> length and strictly better: **check before you insert**, so the current element isn't in the
> map yet and the `!= i` guard becomes unnecessary.
>
> ```python
> seen = {}
> for i, num in enumerate(nums):
>     if target - num in seen:
>         return [seen[target - num], i]
>     seen[num] = i
> ```
>
> One pass, no self-match guard, and it returns as soon as the pair exists instead of after
> building the whole map. Write this one next time.


Two passes. The first builds `value -> index` for the whole array. The second walks the
array again and, for each `number`, asks the map whether its complement `target - number`
was ever seen. Because a dict lookup is `O(1)` average, checking all `n` complements costs
`O(n)` total rather than the `O(n^2)` of comparing every pair by hand.

The `numMap[targetNum] != i` check matters because the map contains the current element
too: with `nums = [3, 2, 4], target = 6`, the complement of `3` is `3` itself, and without
the guard you'd return `[0, 0]`.

Because the map is built first, later duplicates overwrite earlier ones — that's fine here,
since the problem promises exactly one valid answer.

## Mistakes / what to remember

- Hash map = exact-match lookup. Whenever the inner loop of a brute force is just
  "search the array for a specific value", a dict deletes that loop.
- Two passes are correct but one pass also works: insert *after* checking, so the current
  element isn't in the map yet and the self-match guard becomes unnecessary.
- `sol = []` at the top is dead code — worth deleting next time.

## Solution

See [`solution.py`](./solution.py).
