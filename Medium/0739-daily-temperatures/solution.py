"""739. Daily Temperatures (Medium)

https://leetcode.com/problems/daily-temperatures/
Solved 2026-09-16 in 9m.
"""
from typing import List, Optional  # noqa: F401


class Solution(object):
    def dailyTemperatures(self, temperatures):
        #initalize the sol to the same size as temps
        sol = [0] * len(temperatures)
        # a stack would be necessary for the next hotter day when going from left to right
        stack = []
        for i, temp in enumerate(temperatures):
            while stack and temp > stack[-1][0]:
                val, index = stack.pop()
                sol[index] = i - index
            #append the temp and index
            stack.append((temp, i))
        return sol
