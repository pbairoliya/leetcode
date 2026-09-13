"""19. Remove Nth Node From End of List (Medium)

https://leetcode.com/problems/remove-nth-node-from-end-of-list/
Solved 2026-09-12.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        second = head
        i = 0
        while second and i < n:
            i += 1
            second = second.next
        first = dummy = ListNode(0, head)

        while second:
            second = second.next
            first = first.next
        first.next = first.next.next
        return dummy.next
