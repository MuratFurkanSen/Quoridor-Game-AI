"""

from time import sleep

s="|/-\\"

print("Loading....", end="", flush=True)

for i in range(20):
    print(f"\b{s[i%len(s)]}", end="", flush=True)
    sleep(0.5)

"""
"""

class Solution:
    def merge(self, intervals: list[list[int]]):
        i = 0
        intervals.sort()
        while i != len(intervals):

            if i != len(intervals) - 1 and intervals[i][0] <= intervals[i + 1][0] <= intervals[i][1]:
                start = intervals[i][0]
                end = max(intervals[i][1], intervals[i + 1][1])
                intervals.pop(i)
                intervals.pop(i)
                intervals.insert(i, [start, end])
                i -= 1
            i += 1
        return intervals


solution = Solution()
func = solution.merge
print(func([[0, 0], [1, 4]]))
"""


class Solution:
    def twoSum(nums: list[int], target: int) -> list[int]:
        searchList = nums.copy()
        if target > 0:
            searchList.sort()
        else:
            searchList.sort(reverse=True)
        for i in range(len(searchList)):
            if target > 0:
                if target > searchList[i] + searchList[-1]:
                    continue
                if target < searchList[i] + searchList[0]:
                    continue
            else:
                if target > searchList[i] + searchList[0]:
                    continue
                if target < searchList[i] + searchList[-1]:
                    continue
            for j in range(i + 1, len(searchList)):
                if searchList[i] + searchList[j] == target:
                    first = nums.index(searchList[i])
                    nums[first] = target+1 if target > 0 else target-1
                    second = nums.index(searchList[j])
                    result = [first, second]
                    result.sort()
                    return result


A = Solution.twoSum([-3, 4, 3, 90], 0)
print(A)
