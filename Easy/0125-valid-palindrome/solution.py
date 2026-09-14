"""125. Valid Palindrome (Easy)

https://leetcode.com/problems/valid-palindrome/
Solved 2026-09-13.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def alphaNum(self, c):
        c = c.lower()
        if ord('a') <= ord(c) <= ord('z') or ord('0') <= ord(c) <= ord('9'):
            return True
        return False

    def isPalindrome(self, s: str) -> bool:
        left = 0
        right = len(s) - 1
        while left < right:
            while left < right and not self.alphaNum(s[left]):
                left += 1
            while right > left and not self.alphaNum(s[right]):
                right -= 1
            if s[left].lower() != s[right].lower():
                return False

            left += 1
            right -= 1

        return True
