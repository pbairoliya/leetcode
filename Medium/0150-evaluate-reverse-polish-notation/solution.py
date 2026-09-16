"""150. Evaluate Reverse Polish Notation (Medium)

https://leetcode.com/problems/evaluate-reverse-polish-notation/
Solved 2026-09-15.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def evalRPN(self, tokens: List[str]) -> int:
        calculate = []

        for char in tokens:
            if char in ("+","-","*","/"):
                val2 = calculate.pop()
                val1 = calculate.pop()
                newNum = 0
                if char == "+":
                    newNum = val1+val2
                elif char == "-":
                    newNum = val1-val2
                elif char == "*":
                    newNum = val1*val2
                elif char == "/":
                    newNum = int(val1/val2)
                calculate.append(newNum)
            else:
                calculate.append(int(char))
        return calculate[0]
