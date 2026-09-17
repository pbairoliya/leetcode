"""21. Merge Two Sorted Lists (Easy)

https://leetcode.com/problems/merge-two-sorted-lists/
Solved 2026-09-02.
"""
from typing import List, Optional  # noqa: F401


class Solution(object):
    def mergeTwoLists(self, list1, list2):
        newCurr = ListNode(-1, None)
        newHead = newCurr

        if not list1 and not list2:
            return list1

        while list1 and list2:
            if list1.val <= list2.val:
                newCurr.next = list1
                list1 = list1.next
            else:
                newCurr.next = list2
                list2 = list2.next
            newCurr = newCurr.next

        if list1:
            newCurr.next = list1
        elif list2:
            newCurr.next = list2

        return newHead.next
