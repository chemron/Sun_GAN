import matplotlib.pyplot as plt
import os
import plot_specific_magnetogram as mag_plot
plt.switch_backend("agg")

np_dir = "Data/np_HMI_normalised"

png_dir = np_dir + "_png"

v = 4000

print(png_dir)
os.makedirs(png_dir) if not os.path.exists(png_dir) else None

for filename in os.listdir(np_dir):
    mag_plot.plot_magnetogram(f"{np_dir}/{filename}", v)
    name = filename.strip(".npy")
    print(name)
    plt.savefig(f"{png_dir}/{name}.png")
    plt.clf()
