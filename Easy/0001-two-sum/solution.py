"""1. Two Sum (Easy)

https://leetcode.com/problems/two-sum/
Solved 2026-09-03 in 37m.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        sol = []
        numMap = {}
        for i, number in enumerate(nums):
            numMap[number] = i

        for i, number in enumerate(nums):
            targetNum = target - number
            if targetNum in numMap and numMap[targetNum] != i:
                return [i, numMap[targetNum]]

        return []
