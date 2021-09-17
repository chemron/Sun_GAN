import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import copy
import os
plt.switch_backend("agg")

cmap = copy.copy(mpl.cm.get_cmap("seismic"))
cmap.set_bad(color='k')

def get_mask(shape):
    h, w = shape
    center = (int(w/2), int(h/2))
    radius = w/2 + 1
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    mask = dist_from_center <= radius
    return mask


os.makedirs("Plots/") if not os.path.exists("Plots/") else None
filename = input("File path: ")
name = filename.split("/")[-1]
arr = np.load(filename)
v = np.max(np.nan_to_num(np.abs(arr)))
mask = get_mask(arr.shape)
arr[~mask] = np.nan
plt.imshow(arr, cmap=cmap, vmin=-v, vmax=v)
plt.colorbar()
plt.savefig(f"Plots/{name}.png")
