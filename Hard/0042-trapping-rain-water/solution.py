"""42. Trapping Rain Water (Hard)

https://leetcode.com/problems/trapping-rain-water/
Solved 2026-09-15.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def trap(self, height: List[int]) -> int:
        left = 0
        right = len(height) - 1
        leftMax = height[left]
        rightMax = height[right]
        total = 0
        while left < right:
            if height[left] < height[right]:
                left += 1
                leftMax = max(leftMax, height[left])
                total += (leftMax - height[left])

            else:
                right -= 1
                rightMax = max(rightMax, height[right])
                total += (rightMax - height[right])

        return total
