"""128. Longest Consecutive Sequence (Medium)

https://leetcode.com/problems/longest-consecutive-sequence/
Solved 2026-09-13.
"""
from typing import List, Optional  # noqa: F401


class Solution(object):
    def longestConsecutive(self, nums):
        freqMap = {}

        for num in nums:
            freqMap[num] = freqMap.get(num,0) + 1

        maxSol = 0
        for num in nums:
            candidate = num+1
            sol = 1
            while candidate in freqMap:
                candidate += 1
                sol += 1
            maxSol = max(sol, maxSol)

        return maxSol
