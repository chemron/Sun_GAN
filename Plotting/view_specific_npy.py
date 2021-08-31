import numpy as np
import matplotlib.pyplot as plt
plt.switch_backend("agg")

filename = input("File path: ")
name = filename.split("/")[-1]
arr = np.load(filename)
arr = np.nan_to_num(arr)
plt.imsave(f"Plots/{name}.png", arr, cmap="gray")
