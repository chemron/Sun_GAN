from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import argparse

modes = ["AIA", "AIA_normal", "EUVI", "EUVI_normal", "HMI", "HMI_normal", "phase_map", "phase_map_normal"]

q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]

for mode in modes:
    percentiles = np.load(f"Data/np_objects/{mode}_percentiles.npy", allow_pickle=True).T
    plt_dates = np.load(f"Data/np_objects/{mode}_dates.npy", allow_pickle=True)

    # plot percentiles vs dates
    fig, ax = plt.subplots(figsize=(12, 4))

    for i in range(len(percentiles)-1, -1, -1):
        ax.plot_date(plt_dates, percentiles[i],
                        label=f'${q[i]}$th percentile',
                        markersize=1)
    ax.set_ylabel("Pixel Intensity")

    # GET TICkS
    # rule = rrulewrapper(MONTHLY, interval=6)
    # loc = RRuleLocator(rule)
    # ax.xaxis.set_major_locator(loc)
    # formatter = DateFormatter('%m/%y')
    # ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=10)
    ax.set_xlabel("Date")

    # Put a legend to the right of the current axis
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.tight_layout()
    fig.savefig(f"Plots/{mode}_percentiles.png", bbox_inches='tight')
