"""3. Longest Substring Without Repeating Characters (Medium)

https://leetcode.com/problems/longest-substring-without-repeating-characters/
Solved 2026-09-15.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        if len(s) <= 1:
            return len(s)
        left = 0
        subSet = set()
        maxLen = 0

        for right in range(len(s)):
            while s[right] in subSet:
                subSet.remove(s[left])
                left += 1

            subSet.add(s[right])
            maxLen = max(maxLen, right - left + 1)

        return maxLen
