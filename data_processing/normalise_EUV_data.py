from datetime import datetime
from scipy.stats import percentileofscore
import os
import numpy as np
import matplotlib.pyplot as plt
import argparse
from scipy.stats import percentileofscore
plt.switch_backend('agg')



w = h = 1024  # desired width and height of output
# percentiles
q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]

# use n point moving averag to normalise
n=50

def moving_average(a, n):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def remove_outliers(mode):
    # directory of input data
    np_dir = f"DATA/np_{mode}/"

    percentiles = np.load(f"DATA/np_objects/{mode}_percentiles.npy").T
    dates = np.load(f"DATA/np_objects/{mode}_dates.npy")
    datetime_dates = [datetime.strptime(date, "%Y%m%d%H%M%S")
                    for date in dates]

    lower_cutoff, upper_cutoff = get_cutoff(mode, datetime_dates)

    outlier_indicies = np.array(((percentiles[8] < lower_cutoff) |
                                (percentiles[8] > upper_cutoff)))
    outlier_indicies = np.nonzero(outlier_indicies)

    percentiles = np.delete(percentiles, outlier_indicies, 1)
    datetime_dates = np.delete(datetime_dates, outlier_indicies)

    return percentiles, datetime_dates, outlier_indicies


def get_cutoff(mode, datetime_dates):
    upper_cutoff = None
    lower_cutoff = None
    if mode == "AIA":
        upper_cutoff = np.full(len(datetime_dates), np.inf)
        lower_cutoff = np.array([45 if (x < datetime(2014, 1, 1))
                    else 20 if (x < datetime(2015, 2, 1))
                    else 8 for x in datetime_dates])
    elif mode == "EUVI":
        upper_cutoff = np.full(len(datetime_dates), 1300)
        lower_cutoff = np.array([1100 if (x < datetime(2014, 5, 1))
                            else 1070 if (x < datetime(2015, 8, 15))
                            else 1010 if (x < datetime(2016, 12, 1))
                            else 980 if (x < datetime(2018, 4, 1))
                            else 950 for x in datetime_dates])
    else:
        raise ValueError("Mode should be either 'AIA' or 'EUVI'")
    return lower_cutoff, upper_cutoff


def get_AIA_min_p(outlier_indicies, min_p_file n):
    # get percentage of AIA data below 0
    np_dir = f"DATA/np_AIA/"
    data = np.sort(os.listdir(np_dir))
    data = np.delete(data, outlier_indicies)
    data = data[n//2-1:-n//2]
    data = data[n//2-1:-n//2]


    minp = []
    for i in range(len(data) - 1):
        name = data[i]
        filename = np_dir + name
        img = np.load(filename).flatten()
        lower_p = percentileofscore(img, 0)
        print(f"{name}, lower: {lower_p}")
        minp.append(lower_p)

    np.save(min_p_file, np.array(minp))


if __name__ == '__main__':
    # AIA data:
    AIA_p, AIA_dates, AIA_outlier_i = remove_outliers("AIA")

    # get percentage of data below zero for each data
    min_p_file = "DATA/np_objects/AIA_minp"
    if not os.path.isfile(min_p_file):
        get_AIA_min_p(AIA_outlier_i, min_p_file, n)

    # stereo zeros

    # normalise stereo

    # get clip max

    # normalise AIA

#  stereo requires stereo_zeros,
# stereo zeros requires AIA minp
# AIA requires stereo clip max

def normalise_AIA_p():
    mode = "AIA"
    # moving average over 50 images
    n = 50
    np_dir = f"DATA/np_{mode}/"
    normal_np_dir = f"DATA/np_{mode}_normalised/"
    os.makedirs(normal_np_dir) if not os.path.exists(normal_np_dir) else None
    percentiles = np.load(f"DATA/np_objects/{mode}_percentiles.npy").T
    dates = np.load(f"DATA/np_objects/{mode}_dates.npy")

    datetime_dates = [datetime.strptime(date, "%Y%m%d%H%M%S")
                    for date in dates]
    cutoff = np.array([45 if (x < datetime(2014, 1, 1))
                    else 20 if (x < datetime(2015, 2, 1))
                    else 8 for x in datetime_dates])
    outlier_indicies = np.nonzero(percentiles[8] < cutoff)

    percentiles = np.delete(percentiles, outlier_indicies, 1)
    dates = np.delete(dates, outlier_indicies)
    datetime_dates = np.delete(datetime_dates, outlier_indicies)

        
    rolling_75p = moving_average(percentiles[8], n)
    rolling_dates = dates[n//2-1:-n//2]
    percentiles = percentiles.T[n//2-1:-n//2].T
    datetime_dates = datetime_dates[n//2-1:-n//2]
    normal_percentiles = percentiles/rolling_75p

    normal_percentiles = normal_percentiles.clip(None, clip_max)

    normal_percentiles = normal_percentiles/clip_max

    

    normal_percentiles = np.sign(normal_percentiles) * \
                        (np.abs(normal_percentiles)**(1/2))






def normalise_STEREO_p():
    mode = 'STEREO'
    # moving average over 50 images
    n = 50 
    percentiles = np.load(f"DATA/np_objects/{mode}_percentiles.npy").T
    dates = np.load(f"DATA/np_objects/{mode}_dates.npy")
    datetime_dates = [datetime.strptime(date, "%Y%m%d%H%M%S")
                      for date in dates]

    # zero point
zero_point = np.load("DATA/np_objects/STEREO_zeros.npy")
zero_point = np.average(zero_point)
zero_point = int(np.round(zero_point))


"""
TODO:
stereo requires stereo_zeros,
stereo zeros requires AIA minp
AIA requires stereo clip max

"""
