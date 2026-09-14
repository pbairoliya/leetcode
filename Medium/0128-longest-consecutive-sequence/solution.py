"""128. Longest Consecutive Sequence (Medium)

https://leetcode.com/problems/longest-consecutive-sequence/
Solved 2026-09-13.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        numSet = set()
        for num in nums:
            numSet.add(num)
        longest = 0
        for num in numSet:
            if (num - 1) not in numSet:
                length = 1
                while (num + length) in numSet:
                    length += 1

                longest = max(length, longest)

        return longest
