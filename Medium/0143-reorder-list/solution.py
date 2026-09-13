"""143. Reorder List (Medium)

https://leetcode.com/problems/reorder-list/
Solved 2026-09-12 in 20m.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def reorderList(self, head: Optional[ListNode]) -> None:
        # find middle
        slow = head
        fast = head.next
        while fast and fast.next:
            fast = fast.next.next
            slow = slow.next

        # reverse second half
        second = slow.next
        prev = None
        # need to cut the halves
        slow.next = None
        while second:
            nextNode = second.next
            second.next = prev
            prev = second
            second = nextNode

        # merge
        first, second = head, prev

        while second:
            nextOne, nextTwo = first.next, second.next
            first.next = second
            second.next = nextOne
            # move nodes forward now
            first = nextOne
            second = nextTwo
