"""21. Merge Two Sorted Lists (Easy)

https://leetcode.com/problems/merge-two-sorted-lists/
Solved 2026-09-02 in —.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        newCurr = ListNode(-1)
        newHead = newCurr
        curr1 = list1
        curr2 = list2
        while curr1 and curr2:
            if curr1.val < curr2.val:
                newCurr.next = curr1
                curr1 = curr1.next
            else:
                newCurr.next = curr2
                curr2 = curr2.next
            newCurr = newCurr.next

        if curr1:
            newCurr.next = curr1
        else:
            newCurr.next = curr2

        return newHead.next
