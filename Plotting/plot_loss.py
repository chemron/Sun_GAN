import sys
import numpy as np
import matplotlib.pyplot as plt
plt.switch_backend('agg')

n = 500


def moving_average(a, n):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    a[n//2-1:-n//2] = ret[n - 1:] / n
    a[:n//2-1] = a[n//2-1]
    a[-n//2:] = a[-n//2 - 1]
    return a


data = np.loadtxt(sys.argv[1]).T
titles = ["Descriminator Loss",
          "Generator Loss",
          "Generator Absolute Difference"
          ]
fig, axs = plt.subplots(3, 1, figsize=(25, 10))
for i in range(3):
    axs[i].plot(data[0], moving_average(data[i+1], n))
    axs[i].set_title(titles[i])
fig.savefig("Plots/loss.png", bbox_inches='tight')
