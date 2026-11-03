# anon function

lambda num: num * num

#named
squared = lambda n: n * n
print(squared(5))

################################
sum = lambda a,b: a + b
print(sum(12, 12))
################################

def funcBuilder(x):
    return lambda n: x + n

addTen = funcBuilder(10)(7)
addTwenty = funcBuilder(20)(8)
addThirty = funcBuilder(30)
print(addTen)
print(addTwenty)
print(addThirty(30))
##############################

nums = [1,2,3,4,5]
squared_nums = map(lambda x: x**2, nums)
print(squared_nums)
print(list(squared_nums))

#############################
filtered_odd_list = list(filter(lambda x: x%2 != 0, nums))
print(filtered_odd_list)

#############################
from functools import reduce
red_total = reduce(lambda acc,curr: acc + curr, nums, 100)
print(red_total)

#############################
check = [1,2,3,4]
print(*check)