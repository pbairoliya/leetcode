"""9001. Design Double-ended Queue (Easy)

https://neetcode.io/problems/queue
Solved 2026-09-12 in 8m.
"""
from typing import List, Optional  # noqa: F401


class ListNode:
    def __init__(self, val):
        self.val = val
        self.next = None
        self.prev = None


class Deque:

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def isEmpty(self) -> bool:
        # check if size is 0
        if self.size == 0:
            return True
        return False

    def append(self, value: int) -> None:
        newNode = ListNode(value)
        # create new node
        if self.isEmpty():
            self.head = self.tail = newNode
        else:
            end = self.tail
            end.next = newNode
            newNode.prev = end
            self.tail = newNode

        # increase linked list size
        self.size += 1

    def appendleft(self, value: int) -> None:
        newNode = ListNode(value)
        # create new Node
        if self.isEmpty():
            self.head = self.tail = newNode
        else:
            self.head.prev = newNode
            newNode.next = self.head
            # new head should connect to the old head
            self.head = newNode
            # move head to the start which would be new node
        self.size += 1
        # increase size

    def pop(self) -> int:
        if self.isEmpty():
            return -1
        val = self.tail.val
        self.tail = self.tail.prev
        self.size -= 1
        return val

    def popleft(self) -> int:
        if self.isEmpty():
            return -1
        val = self.head.val
        self.head = self.head.next
        self.size -= 1
        return val
