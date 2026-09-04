"""206. Reverse Linked List (Easy)

https://leetcode.com/problems/reverse-linked-list/
Solved 2026-09-02 in —.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        prev, curr = None, head
        while curr:
            nextNode = curr.next
            curr.next = prev
            prev = curr
            curr = nextNode
        return prev
