import sys
import numpy as np

a = np.array([1, 2, 3, 4, 5])
b = np.array([5, 2, 3, 4, 1])
for v in b:
    v += 1
print(b)
c = [1] * 5
d = f = 1
e = 2
d, e = e, f
print("%d %d %d" %(id(d), id(e), id(f)))