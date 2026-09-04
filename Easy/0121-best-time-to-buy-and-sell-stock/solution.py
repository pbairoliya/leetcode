"""121. Best Time to Buy and Sell Stock (Easy)

https://leetcode.com/problems/best-time-to-buy-and-sell-stock/
Solved 2026-09-03 in 18m.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        best, cheapest = 0, float("inf")
        for price in prices:
            cheapest = min(cheapest, price)
            best = max(best, price - cheapest)
        return best
