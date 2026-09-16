"""567. Permutation in String (Medium)

https://leetcode.com/problems/permutation-in-string/
Solved 2026-09-15.
"""
from typing import List, Optional  # noqa: F401


class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        if len(s2) < len(s1):
            return False

        #first make a frequency counter of s1
        s1Freq = {}
        for letter in s1:
            s1Freq[letter] = s1Freq.get(letter, 0) + 1

        s2Freq = {}
        left = 0
        #only when the right -left+1 matches the length then return true
        for right in range(len(s2)):
            #add letters to the second freq map
            s2Freq[s2[right]] = s2Freq.get(s2[right], 0) + 1
            #if the size is bigger then s1 we gotta delete
            if right - left + 1 > len(s1):
                s2Freq[s2[left]] -= 1
                if s2Freq[s2[left]] == 0:
                    del s2Freq[s2[left]]
                left += 1
            # if the two match then bam we gucci
            if s1Freq == s2Freq:
                return True

        return False
