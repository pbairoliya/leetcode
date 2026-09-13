# 347. Top K Frequent Elements

[Problem on LeetCode](https://leetcode.com/problems/top-k-frequent-elements/)

| | |
|---|---|
| **Difficulty** | 🟡 Medium |
| **Topics** | `Array`, `Hash Table`, `Divide and Conquer`, `Sorting`, `Heap (Priority Queue)`, `Bucket Sort`, `Counting`, `Quickselect` |
| **Time to solve** | 8m |
| **Attempts** | 1 |
| **Solved** | 2026-09-12 |

## My approach

Same first move as [[0001 Two Sum]]: the question "how many times does this value appear?"
is an exact-key lookup, so a hash map counts frequencies in one `O(n)` pass.

The second half is the actual problem: I have counts and I need the `k` largest. The obvious
answer is to sort the counts, `O(n log n)`, or use a heap, `O(n log k)`. But a count is
bounded — a value can appear at most `n` times — so the counts are small integers in a known
range, and a sort isn't needed at all. That's the cue for **bucket sort**.

## Complexity

**Time:** `O(n)`  
**Space:** `O(n)`

## Explanation

### What bucket sort actually is

Bucket sort is a **non-comparison** sort. Instead of asking "is a bigger than b?" over and
over, it uses the value itself as an address:

1. Create an array of empty buckets, one per possible value (or per value range).
2. Scatter — drop each item into the bucket its value points at. That's `O(1)` per item,
   because indexing an array is `O(1)`.
3. Gather — walk the buckets in index order and read the items back out. They come out
   sorted, because bucket order *is* value order.

Cost is `O(n + m)` where `n` is the number of items and `m` the number of buckets. It beats
the `O(n log n)` comparison-sort lower bound only because it doesn't compare — it requires
the keys to be integers in a small, known range. If `m` is huge relative to `n` (say,
sorting arbitrary 64-bit numbers), you'd allocate a galaxy of empty buckets and it loses.

### Why it fits here

Sorting by frequency is exactly that special case. A frequency is an integer, and it can
never exceed `len(nums)` — so `len(nums) + 1` buckets cover every possible count, and `m` is
`O(n)`. The bucket *index* is the frequency and the bucket *contents* are the values that
occur that often:

```
nums = [1,1,1,2,2,3]          counts = {1: 3, 2: 2, 3: 1}

index:     0    1    2    3
bucket:   []   [3]  [2]  [1]
                            ^ walk from the right, take k
```

Walking the buckets from the highest index down yields values in descending frequency
order, and I stop the moment `sol` holds `k` of them. Every step is linear — count, scatter,
gather — so the whole thing is `O(n)` time and `O(n)` space, beating both the sort
(`O(n log n)`) and the heap (`O(n log k)`).

The early `return sol` inside the inner loop is what keeps the gather cheap; the trailing
`return sol` can't actually be reached, since the buckets always hold at least `k` distinct
values when the input is valid.

## Mistakes / what to remember

- `range(len(nums) + 1)`, not `len(nums)` — a value can appear all `n` times, so index `n`
  has to exist.
- Bucket sort's precondition is "keys are integers in a small known range". Frequencies
  always satisfy it; raw input values usually don't. Check that before reaching for it.
- Reach for buckets when the ranking key is bounded; reach for a heap when it isn't, or
  when the data is streaming and `k` is tiny.

## Solution

See [`solution.py`](./solution.py).
