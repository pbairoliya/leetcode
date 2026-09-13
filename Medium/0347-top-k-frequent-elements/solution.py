"""347. Top K Frequent Elements (Medium)

https://leetcode.com/problems/top-k-frequent-elements/
Solved 2026-09-12 in 8m.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        numMap = {}
        for num in nums:
            numMap[num] = numMap.get(num, 0) + 1

        sol = []
        bucketSort = [[] for _ in range(len(nums) + 1)]
        for key, value in numMap.items():
            bucketSort[value].append(key)

        for i in range(len(bucketSort) - 1, -1, -1):
            for key in bucketSort[i]:
                sol.append(key)
                if len(sol) == k:
                    return sol

        return sol
