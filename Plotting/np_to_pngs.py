import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import copy
import os
plt.switch_backend("agg")

np_dir = "Data/UV_GAN_1_on_EUVI/ITER0300000"
np_dir = "Data/np_HMI_normalised"
np_dir = "Data/UV_GAN_1_on_AIA/ITER0300000"
v = 4000

png_dir = np_dir + "_png"

clip_max = np.load("Data/np_objects/HMI_clip_max.npy")

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


def to_png(filename, v):
    arr = np.load(f"{np_dir}/{filename}")
    arr = np.sign(arr) * np.abs(arr)**2
    arr *= clip_max

    arr[~mask] = np.nan
    plt.imshow(arr, cmap=cmap, vmin=-v, vmax=v)
    plt.colorbar()

    name = filename.strip(".npy")
    print(name)
    plt.savefig(f"{png_dir}/{name}.png")
    plt.clf()


mask = get_mask((1024, 1024))
print(png_dir)
os.makedirs(png_dir) if not os.path.exists(png_dir) else None

for filename in os.listdir(np_dir):
    to_png(filename, v)
