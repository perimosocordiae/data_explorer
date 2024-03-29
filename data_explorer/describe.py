#!/usr/bin/env python3
import sys
import numpy as np
from scipy.stats import describe

np.set_printoptions(suppress=True, precision=3)

data = np.loadtxt(sys.stdin)
count, minmax, mean, var = describe(data)[:4]
q1, median, q3 = np.percentile(data, (25, 50, 75), overwrite_input=True)

headers = ["n", "mean", "var", "min", "q1", "median", "q3", "max"]
stats = np.array([count, mean, var, minmax[0], q1, median, q3, minmax[1]])
stats = str(stats)[1:-1].split()

for i, header in enumerate(headers):
    n = max(len(header), len(stats[i]))
    headers[i] = header.ljust(n)
    stats[i] = stats[i].ljust(n)

print("  ".join(headers))
print("  ".join(stats))
