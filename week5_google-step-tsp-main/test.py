import itertools

lis = [2, 3, 1, 4]
for (i, j) in itertools.combinations(lis, 2):
	print(i, j)

lis.sort()
print(lis)
