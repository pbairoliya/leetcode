"""739. Daily Temperatures (Medium)

https://leetcode.com/problems/daily-temperatures/
Solved 2026-09-16.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        res = [0] * len(temperatures)
        stack = []                                   # indices waiting for a warmer day

        for i, temp in enumerate(temperatures):
            while stack and temperatures[stack[-1]] < temp:
                j = stack.pop()
                res[j] = i - j                       # today is the day j was waiting for
            stack.append(i)

        return res
