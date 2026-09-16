# 239. Sliding Window Maximum

[Problem on LeetCode](https://leetcode.com/problems/sliding-window-maximum/)

| | |
|---|---|
| **Difficulty** | 🔴 Hard |
| **Topics** | `Array`, `Queue`, `Sliding Window`, `Heap (Priority Queue)`, `Monotonic Queue`, `Range Minimum/Maximum Query` |
| **Time to solve** | — |
| **Attempts** | 1 |
| **Solved** | 2026-09-15 |
| **Unaided** | no |

## My approach

Reached for the fixed-window template from [[0567 Permutation in String]] with a heap as the
window state. **The template was right; the state wasn't.**

The thing this problem taught me:

> **A sliding window only works if the window's state can be *undone* as cheaply as it was
> done.** Sums, counts and frequency maps are invertible — subtract what leaves. **A maximum
> is not.** Once you've folded a value into a running max, there is no way to un-fold the
> element that just left the window.

So the question isn't "how do I maintain the max?", it's **"how do I keep enough *candidates*
around that the max is always available?"** Two answers below.

## Complexity

**Time:** `O(n)` for the deque; `O(n log n)` for the lazy heap  
**Space:** `O(k)` for the deque; `O(n)` worst case for the heap

## Explanation

### Three separate bugs, worth separating

**1. `heap.pop()` is `list.pop()`, not `heapq.heappop()`.**
A Python heap *is* a plain list, so `.pop()` compiles fine and silently removes the **last
element of the internal array** — an arbitrary leaf, not the smallest, not the largest, not
the one you wanted. `heap[0]` is the min; **`heap[-1]` means nothing.** This is the single
nastiest `heapq` trap: nothing errors, the structure just quietly stops meaning what you
think.

**2. Even `heapq.heappop(heap)` would be wrong.**
That removes the *largest* value (you negated), but the element leaving the window is
`nums[left]`, which is usually somewhere in the middle. **A binary heap has no `O(log n)`
"delete this particular item".** That's not a gap in `heapq` — it's the data structure.

**3. The pair should be `(-value, index)`, not `(-value, value)`.**
Storing the value twice tells you nothing new. The **index** is what lets you ask "is this
entry still inside the window?", which is the whole trick in Fix A.

### The real lesson: invertible vs. not

The fixed-window template is

```python
add(arr[right])
if right >= k: remove(arr[right - k])
```

and it quietly assumes `remove` **exists and is cheap**. Check that before you commit:

| window state | can you undo it? | how |
|---|---|---|
| sum | ✅ | `total -= leaving` |
| count / frequency map | ✅ | decrement the key (delete at zero) |
| number of distinct | ✅ | via the frequency map |
| **max / min** | ❌ | you can't un-fold a `max` |
| **k-th largest, median** | ❌ | needs a richer structure |

**When the aggregate isn't invertible, stop maintaining an answer and start maintaining
candidates.** Two ways:

- **Lazy deletion** — keep stale entries, and discard them only when they surface at the top
  and you can see they're out of range. Each element is pushed once and popped at most once,
  so the amortised cost stays `O(log n)`. This is the general escape hatch for "heap needs a
  delete it doesn't have".
- **Monotonic deque** — never let a doomed candidate in.

### Why the deque works — the same discard argument, a fourth time

> If `j < i` and `nums[j] <= nums[i]`, then `j` is **older and no bigger**. Every future
> window containing `j` also contains `i`, and `i` is at least as large — so `j` can never be
> an answer again. Delete it forever.

That's the exact shape of the argument from [[0167 Two Sum II - Input Array Is Sorted]],
[[0011 Container With Most Water]] and [[0042 Trapping Rain Water]]: *this candidate's best
possible case already loses, so discard it.*

What survives is a deque of indices whose values are **strictly decreasing**. The front is
the largest — the window max — and the rest are the next-in-line successors, kept in case the
front ages out.

```
nums = [1,2,1,0,4,2,6], k = 3      (deque shown as values)

right=0  [1]              -
right=1  2 kills 1 → [2]  -
right=2  [2,1]            window [1,2,1] → 2
right=3  [2,1,0]          window [2,1,0] → 2
right=4  4 kills 0,1,2 → [4]   window [1,0,4] → 4
right=5  [4,2]            window [0,4,2] → 4
right=6  6 kills 2,4 → [6]     window [4,2,6] → 6
```

Every index is appended once and removed once, so despite the inner `while` it's `O(n)` —
the same aggregate argument as [[0003 Longest Substring Without Repeating Characters]].

**Why `<=` and not `<`** in `nums[dq[-1]] <= nums[right]`: with equal values, the older one is
strictly worse (it expires sooner and is no larger), so dropping it is safe and keeps the
deque smaller. `<` also produces a correct answer — it just keeps duplicates around.

### Small things

- **You don't need `left`.** In a fixed window it's always `right - k + 1`; `right >= k - 1`
  and `right - k` say everything. (Same note as [[0567 Permutation in String]].)
- **`if right - left + 1 == k` only ever fires once** in the original, because `left` advances
  in lockstep from then on — fine, but `right >= k - 1` is the idiom.

## Mistakes / what to remember

- **Before using the fixed-window template, ask: can the window state be *undone*?** Sums,
  counts and frequency maps can (subtract what leaves). **Max, min, median, k-th largest
  cannot.** That question is the whole difficulty of this problem.
- **When the aggregate isn't invertible, maintain *candidates*, not an answer.**
- **`heap.pop()` is `list.pop()`** — it removes an arbitrary leaf and silently corrupts your
  reasoning. Use `heapq.heappop()`. `heap[0]` is the min; **`heap[-1]` is meaningless.**
- **A binary heap cannot delete an arbitrary element.** Use **lazy deletion**: store
  `(priority, index)`, leave stale entries in, and pop them only when they reach the top and
  prove to be out of window. Amortised `O(log n)`, and it's the general fix.
- **Monotonic deque:** *older and no bigger ⇒ dead forever.* Keep indices with strictly
  decreasing values; front = window max; pop the front when `dq[0] <= right - k`. `O(n)`,
  because each index enters and leaves exactly once.
- Store the **index** in the heap/deque, not the value again — the index is what tells you
  whether an entry is still in the window.
- A solution that passes the sample can still be wrong on **half** of random inputs. Check
  `k == 1` and a decreasing array before trusting it.

## Solution

See [`solution.py`](./solution.py).
