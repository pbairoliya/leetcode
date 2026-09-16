"""239. Sliding Window Maximum (Hard)

https://leetcode.com/problems/sliding-window-maximum/
Solved 2026-09-15.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        sol = []
        heap = []
        left = 0
        for right in range(0, len(nums)):
            heapq.heappush(heap, (-nums[right], nums[right]))
            if right - left + 1 == k:
                left += 1
                heap.pop()
                sol.append(-heap[0][0])

        return sol
