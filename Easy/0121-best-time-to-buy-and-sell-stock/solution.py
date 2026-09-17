"""121. Best Time to Buy and Sell Stock (Easy)

https://leetcode.com/problems/best-time-to-buy-and-sell-stock/
Solved 2026-09-03 in 18m.
"""
from typing import List, Optional  # noqa: F401


class Solution(object):
    def maxProfit(self, prices):
        profitMax = 0
        bestBuy = float("inf")

        for price in prices:
            if price > bestBuy:
                profit = price - bestBuy
                profitMax = max(profit, profitMax)
            bestBuy = min(bestBuy, price)

        return profitMax
