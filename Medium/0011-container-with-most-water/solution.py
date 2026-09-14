"""11. Container With Most Water (Medium)

https://leetcode.com/problems/container-with-most-water/
Solved 2026-09-13.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def maxArea(self, heights: List[int]) -> int:
        left, right = 0, len(heights) - 1
        best = 0

        while left < right:
            area = (right - left) * min(heights[left], heights[right])
            best = max(best, area)

            if heights[left] < heights[right]:
                left += 1
            else:
                right -= 1

        return best
