# 739. Daily Temperatures

[Problem on LeetCode](https://leetcode.com/problems/daily-temperatures/)

| | |
|---|---|
| **Difficulty** | 🟡 Medium |
| **Topics** | `Array`, `Stack`, `Monotonic Stack` |
| **Time to solve** | — |
| **Attempts** | 1 |
| **Solved** | 2026-09-16 |
| **Unaided** | no |

## My approach

> [!danger] Did not solve this one. **Redo it from a blank file.**
> I knew "stack" only because of the category, and could not derive it. Read the Explanation,
> close the note, and rewrite both versions from scratch. Review date is set short on purpose.

**The reframe I missed:** "how many days until it's warmer" is *not* really a counting
question. It's **"find the next greater element to the right"**, and then subtract indices.
Recognising that renames the problem into one with a standard answer.

**My instinct to go backwards was right** — it just needed a stack to go with it. Both
directions work, and the note below has both.

## Complexity

**Time:** `O(n)` — each index is pushed once and popped once  
**Space:** `O(n)`

## Explanation

### Deriving the stack instead of remembering it

Run the deferred-work question from §4 of [[Leetcode Study Guide]]:

**1. Walking left to right, can I answer day `i` when I reach it?**
No — the answer is in the future. So day `i` becomes a **parked obligation**: *"waiting for
someone warmer."*

**2. When day `j` shows up, which parked days does it discharge?**
Every parked day cooler than `temperatures[j]`.

**3. In what order?** — this is the step that names the structure.
**The most recently parked first.** And here's the part that makes it click:

> **The days still waiting are always in decreasing temperature order.**

That isn't a rule I impose — it's forced. If an older waiting day were *cooler* than a newer
waiting day, the newer day would already have discharged it when it arrived. So a cooler day
can never sit behind a warmer one in the waiting list.

Most-recent-first ⇒ **stack**. The "monotonic" part is a *consequence*, not a design choice.

### The picture

The stack is a staircase descending to the right — each waiting day cooler than the one
before it. A warm day walks up that staircase from the top of the stack downward, knocking
off every step shorter than it, and then takes its own place at the top.

```
temperatures = [30, 38, 30, 36, 35, 40, 28]

i=0  30                      stack(temps): [30]
i=1  38  knocks off 30       res[0] = 1-0 = 1     stack: [38]
i=2  30                      stack: [38,30]
i=3  36  knocks off 30       res[2] = 3-2 = 1     stack: [38,36]
i=4  35                      stack: [38,36,35]
i=5  40  knocks off 35,36,38 res[4]=1, res[3]=2, res[1]=4   stack: [40]
i=6  28                      stack: [40,28]

left waiting: 40, 28 → res stays 0 for both
res = [1,4,1,2,1,0,0] ✓
```

**Whatever is still on the stack at the end never found an answer** — which is exactly why
initialising `res` to all zeros handles the "no warmer day" case with no extra code. Asking
*"what does a leftover stack mean?"* is a standard step with stacks.

### Why it's `O(n)` with a `while` inside a `for`

Each index is pushed exactly once and popped **at most** once, so the total number of inner
iterations across the whole run is `≤ n`. **Count total pushes and pops, not loop nesting** —
the same aggregate argument as [[0128 Longest Consecutive Sequence]],
[[0003 Longest Substring Without Repeating Characters]] and [[0239 Sliding Window Maximum]].

### The two directions, and why the comparison flips

| | forward | backward |
|---|---|---|
| the stack holds | days **waiting** for an answer | days that could **be** an answer |
| you write `res[...]` | when a day is **popped** | when a day is **pushed** |
| pop condition | `stack top < current` | `stack top <= current` |

The flip is not arbitrary. **Forward:** you pop a waiting day when today is *strictly*
warmer — an equal day is not "warmer", so it must stay parked. **Backward:** you discard a
candidate that is *not strictly warmer than you* — an equal day can never be your answer, so
`<=` throws it out.

Getting `<` and `<=` backwards is the standard bug in this family, and ties are what expose
it. **Always test an input with repeated values.**

### The family this belongs to

One pass, one stack, four questions:

| want | direction | pop while |
|---|---|---|
| next **greater** to the right | forward | `top < current` |
| next **smaller** to the right | forward | `top > current` |
| previous **greater** | forward | `top <= current`, then peek before pushing |
| previous **smaller** | forward | `top >= current`, then peek before pushing |

A bonus worth knowing: in the forward version, **at the moment you push `i`, whatever is on
top of the stack is `i`'s previous-greater element.** One pass gives you both directions.

Same machinery solves Next Greater Element I/II, Largest Rectangle in Histogram, Sum of
Subarray Minimums, and Car Fleet.

## Mistakes / what to remember

- **Rename the question first.** "How many days until warmer" = **next greater element to the
  right**, then subtract indices. The counting is a detail; the search is the problem.
- **Derive the stack, don't recall it:** *I can't answer day `i` now → park it. A warm day
  discharges the parked days cooler than it. The parked days are necessarily in decreasing
  order (a cooler one could never sit behind a warmer one), so the newest is discharged
  first.* Newest-first ⇒ stack, and monotonic falls out on its own.
- **Both directions work.** Forward: the stack holds days *waiting*, and you write the answer
  when you **pop**. Backward: the stack holds *candidates*, and you write the answer when you
  **push**.
- **The comparison flips between them** — forward pops on `<` (equal isn't warmer, stay
  parked), backward pops on `<=` (equal can never be my answer). **Ties are the test case
  that catches this.**
- **Whatever is left on the stack never got an answer** — pre-fill the result with the
  default and you need no cleanup pass.
- `O(n)` despite the nested `while`: each index is pushed once and popped at most once.
- Bonus: when you push `i` in the forward version, the current stack top is `i`'s
  **previous greater** element. One pass, two answers.

## Solution

See [`solution.py`](./solution.py).
