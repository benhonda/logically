import itertools

l = [False, True]
l2 = list(itertools.product(l, repeat=5))
print(l2)
print(len(l2))

