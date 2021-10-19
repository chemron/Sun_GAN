import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import copy
import os
plt.switch_backend("agg")


def get_mask(shape):
    h, w = shape
    center = (int(w/2), int(h/2))
    radius = w/2 + 1
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    mask = dist_from_center <= radius
    return mask


def plot_magnetogram(filename, v, colorbar=True):
    arr = np.load(filename)
    arr = np.sign(arr)*(arr**2)
    arr *= clip_max
    arr[~mask] = np.nan
    plt.imshow(arr, cmap=cmap, interpolation='none', vmin=-v, vmax=v)
    plt.axis('off')
    del arr
    if colorbar:
        cbar = plt.colorbar(ax=plt.gca(), shrink=0.8)
        cbar.set_label(r"Magnetic Field Strength [$G$]")


mask = get_mask((1024, 1024))
clip_max = np.load("Data/np_objects/HMI_clip_max.npy")
cmap = copy.copy(mpl.cm.get_cmap("seismic"))
cmap.set_bad(color='k')


if __name__ == '__main__':
    os.makedirs("Plots/") if not os.path.exists("Plots/") else None
    filename = input("File path: ")
    name = filename.split("/")[-1]
    v = 4000
    plt.title(r"Predicted line-of-sight Magnetic field [$G$]")
    plot_magnetogram(filename, v)
    plt.savefig(f"Plots/{name}.png", dpi=300)
