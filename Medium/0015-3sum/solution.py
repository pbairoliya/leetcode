"""15. 3Sum (Medium)

https://leetcode.com/problems/3sum/
Solved 2026-09-13.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        sol = []
        nums.sort()
        for i in range(len(nums)):
            if i > 0 and nums[i] == nums[i-1]:
                continue
            left = i+1
            right = len(nums)-1
            while left < right:
                if nums[i] + nums[left] + nums[right] == 0 and [i,left,right] not in sol:
                    sol.append([nums[i],nums[left],nums[right]])
                    left +=1
                    right -=1
                    while nums[left] == nums[left-1] and left < right:
                        left +=1
                if nums[i] + nums[left] + nums[right] >0:
                    right -=1
                if nums[i] + nums[left] + nums[right] <0:
                    left +=1

        return sol
