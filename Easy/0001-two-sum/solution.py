"""1. Two Sum (Easy)

https://leetcode.com/problems/two-sum/
Solved 2026-09-03 in 37m.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}
        for i, n in enumerate(nums):
            if target - n in seen:
                return [seen[target - n], i]
            seen[n] = i
        return []
