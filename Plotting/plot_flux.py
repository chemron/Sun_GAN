import sys
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, DAILY, DateFormatter,
                              rrulewrapper, RRuleLocator)
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--data",
                    nargs='+',
                    help="sql column of data paths to use ",
                    default=[
                        'aia.UV_GAN_1_iter_0000020_path',
                        'euvi.UV_GAN_1_iter_0000020_path',
                        'hmi.np_path_normal',
                        'phase_map.Seismic_GAN_1_iter_0000020_path'
                    ]
                    )

args = parser.parse_args()



def moving_average(fluxes, dates, dt):
    av_flux = np.zeros_like(fluxes)
    for i, date in enumerate(dates):
        indices = np.where(abs(dates - date) < dt)[0]
        print(type(fluxes), fluxes)
        print(indices)
        print(fluxes[indices])
        av_flux[i] = np.average(fluxes[indices])

    return av_flux



def get_data(path):
    fluxes, dates = np.load(path)
    fluxes = fluxes.astype('float64')
    dates = np.array([datetime.strptime(time, "%Y.%m.%d_%H:%M:%S")
                      for time in dates])
    
    dt = timedelta(days=27.2/2)
    av_fluxes = moving_average(fluxes, dates, dt)

    return dates, fluxes, av_fluxes


# def plot_flares(ax):
#     # plot flares
#     x_flares = open(f"{folder}x_flare_list.txt", "r")
#     x_dates = []
#     for line in x_flares:
#         y, m, d = line.split("/")
#         y = int(y)
#         m = int(m)
#         d = int(d[:-1])
#         x_dates.append(datetime(year=y, month=m, day=d))
#     x_flares.close
#     n_x = len(x_dates)
#     for i in range(n_x):
#         x_date = x_dates[i]
#         ax.axvline(x_date, c='tab:gray', label="x class flare" if i==0 else "", linestyle='--', alpha=1, zorder=0)


def find_nearest(array, value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or abs(value - array[idx-1]) < abs(value - array[idx])):
        return idx-1, array[idx-1]
    else:
        return idx, array[idx]

# set up figure
fig, ax = plt.subplots(1, figsize=(15, 8))
# rule = rrulewrapper(MONTHLY, interval=6)
# loc = RRuleLocator(rule)
# ax.xaxis.set_major_locator(loc)
formatter = DateFormatter('%d/%m/%y')
ax.xaxis.set_major_formatter(formatter)
ax.xaxis.set_tick_params(rotation=30, labelsize=10)
ax.set_xlabel("Date [day/month/year]")
ax.set_ylabel(r"Flux [$G.m^2 \times 10^{19}$]")
# ax.set_ylim(2e19, 8e19)
# ax.set_ylim(1e18, 1e21)
# colours
# cmap = list(plt.get_cmap("tab10").colors)
cmap = [
    'lightblue', 'navajowhite', 'mediumseagreen', 'lightcoral', 'plum',
    'sandybrown', 'pink', 'lightgray', 'khaki', 'powderblue'
    ]
c = 0

# if flares:
#     plot_flares(ax)


for i, data_type in enumerate(args.data):
    if i == 10:
        print("Not enough colours for >9 plots!")
        break
    instrument, mode = data_type.split(".")
    save_path = f"Data/unsigned_flux/flux_{instrument}_{mode}.npy"
    label = instrument.upper().replace("_", " ") + " magnetogram"
    date, flux, av_flux = get_data(save_path)
    plt.scatter(date, flux/1e19, label=f"Flux according to {label}", s=4, alpha=0.8,color=cmap[i], zorder=10)
    plt.plot(date, av_flux/1e19, label=f"27 day average flux according to {label}", zorder=10)


# title_str = "Total Unsigned Magnetic Flux vs Time"
# if average:
#     title_str += " with ~27 day rolling average"
# plt.title(title_str)

plt.tight_layout
plt.legend()


plt.savefig("Plots/fluxes.png", dpi=300)


# fig.set_size_inches(6, 10)
# start = datetime(2012, 7, 15)
# end = datetime(2012, 7, 25)
# plt.xlim(start, end)
# plt.savefig(f"peaktrough", dpi=300)

