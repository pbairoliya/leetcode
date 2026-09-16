"""20. Valid Parentheses (Easy)

https://leetcode.com/problems/valid-parentheses/
Solved 2026-09-15.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def isValid(self, s: str) -> bool:
        brackets = {")":"(", "]":"[", "}":"{"}
        stack = []

        for char in s:
            if char in brackets.values():
                stack.append(char)
            else:
                if not stack or stack.pop() != brackets[char]:
                    return False

        if len(stack) != 0:
            return False
        return True
