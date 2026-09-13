"""206. Reverse Linked List (Easy)

https://leetcode.com/problems/reverse-linked-list/
Solved 2026-09-02.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        reverse = None
        curr = head

        while curr:
            nextNode = curr.next
            curr.next = reverse
            reverse = curr
            curr = nextNode

        return reverse
