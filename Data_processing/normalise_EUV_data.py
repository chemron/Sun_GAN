from datetime import datetime
from scipy.stats import percentileofscore
import os
import numpy as np
import matplotlib.pyplot as plt
import argparse
from scipy.stats import percentileofscore
import cv2

plt.switch_backend('agg')



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
    np_dir = f"Data/np_{mode}/"

    percentiles = np.load(f"Data/np_objects/{mode}_percentiles.npy").T
    datetime_dates = np.load(f"Data/np_objects/{mode}_dates.npy")

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


def get_AIA_min_p(outlier_indicies, min_p_file, n):
    # get percentage of AIA data below 0
    np_dir = f"Data/np_AIA/"
    data = np.sort(os.listdir(np_dir))
    data = np.delete(data, outlier_indicies)

    minp = []
    for i in range(len(data) - 1):
        name = data[i]
        filename = np_dir + name
        img = np.load(filename).flatten()
        lower_p = percentileofscore(img, 0)
        print(f"{name}, lower: {lower_p}")
        minp.append(lower_p)

    np.save(min_p_file, np.array(minp))


def get_EUVI_zeros(min_p_file, EUVI_zeros_file, outlier_indicies):
    data_dir = "Data/np_EUVI/"
    data = np.sort(os.listdir(data_dir))
    data = np.delete(data, outlier_indicies)

    # percentiles of 0 in AIA data (what percentile zero occurs at)
    AIA_zero_ps = np.load(f"{min_p_file}.npy")
    # average zero:
    av_AIA_zero_p = np.average(AIA_zero_ps)
    EUVI_zeros = []

    # get equivalent zero:
    for i in range(len(data)):
        name = data[i]
        print(name)
        filename = data_dir + name
        img = np.load(filename).flatten()
        EUVI_zero = np.percentile(img, av_AIA_zero_p)
        EUVI_zeros.append(EUVI_zero)

    np.save(EUVI_zeros_file, np.array(EUVI_zeros))

# rolling max
def get_clip_max(lst, k):
    # get the minimum of 50 point rolling max's
    clip_max = np.inf
    for local_max in rolling_list(lst, k):
        if local_max < clip_max:
            clip_max = local_max
    return clip_max

def rolling_list(lst, k):
    n = len(lst)
    current_lst = lst[:k]
    for i in range(n):
        if (i > k) and (i < n-k):
            right = min(i + k//2, n)
            left = max(0, right - k)
            current_lst = lst[left:right]

        yield max(current_lst)

def normalise_EUVI_p(zero_point, percentiles, datetime_dates):
    # normalise the percentiles of EUVI data

    # adjust to match AIA zero point
    percentiles -= zero_point

    # rolling average of 75th percentile
    rolling_75p = moving_average(percentiles[8], n)
    percentiles = percentiles.T[n//2-1:-n//2].T
    datetime_dates = datetime_dates[n//2-1:-n//2]

    # Divide by 75th percentile to account for decreasing saturation
    normal_percentiles = percentiles/rolling_75p

    clip_max = get_clip_max(normal_percentiles[-1], 50)


    return rolling_75p, clip_max


def normalise_data(mode, rolling_75p, clip_max, outlier_indicies, zero_point):
    w = h = 1024  # desired width and height of output
    np_dir = f"Data/np_{mode}/"
    normal_np_dir = f"Data/np_{mode}_normalised/"
    os.makedirs(normal_np_dir) if not os.path.exists(normal_np_dir) else None

    data = np.sort(os.listdir(np_dir))
    data = np.delete(data, outlier_indicies)
    data = data[n//2-1:-n//2]
    print(len(data))
    print(len(rolling_75p))
    assert len(rolling_75p) == len(data)

    # normal percentiles and corresponding dates
    normal_p = []
    normal_d = []                                                           


    for i in range(len(data)):

        # what we need to divide by to normalise with clip_max at 1
        name = data[i]
        date_str = name.split('_')
        date_str = date_str[1] + date_str[2]
        date = datetime.strptime(date_str, '%Y.%m.%d%H:%M:%S.npy')
        save_name = f'{mode}_{date.year}.{date.month:0>2}.{date.day:0>2}_' \
                    f'{date.hour:0>2}:{date.minute:0>2}:{date.second:0>2}'
        divider = rolling_75p[i] * clip_max
        filename = np_dir + name
        img = np.load(filename)
        img -= zero_point
        img = img/divider
        img = img.clip(0, 1)

        # square root data to increase saturation (see thesis)
        img = (np.abs(img) ** (1/2))
        try:
            img = cv2.resize(img, dsize=(w, h))
            np.save(normal_np_dir + save_name, img)
        except cv2.error as e:
            print(f"{name}: {e}")

        try:
            percentiles = np.percentile(img, q)
            if percentiles is not None:
                normal_p.append(percentiles)
                normal_d.append(date)
        except IndexError as e:
            print(f"{name}: {e}")


    percentile_dir = "Data/np_objects/"
    os.makedirs(percentile_dir) if not os.path.exists(percentile_dir) else None

    np.save(f"{percentile_dir}{mode}_normal_percentiles", normal_p)
    np.save(f"{percentile_dir}{mode}_normal_dates", normal_d)
            

if __name__ == '__main__':
    # AIA data:
    AIA_p, AIA_dates, AIA_outlier_i = remove_outliers("AIA")
    EUVI_p, EUVI_dates, EUVI_outlier_i = remove_outliers("EUVI")

    # get percentage of data below zero for each data
    min_p_file = "Data/np_objects/AIA_minp"
    if not os.path.isfile(min_p_file):
        get_AIA_min_p(AIA_outlier_i, min_p_file, n)
    # get percentile of EUVI data that matches the AIA zeros
    EUVI_zeros_file = "Data/np_objects/EUVI_zeros"
    if not os.path.isfile(EUVI_zeros_file):
        get_EUVI_zeros(min_p_file, EUVI_zeros_file, EUVI_outlier_i)

    zero_point = np.load(f"{EUVI_zeros_file}.npy")
    zero_point = np.average(zero_point)
    zero_point = int(np.round(zero_point))
    # get rolling average of 75th percentile, clip max
    EUVI_rolling_75p, clip_max = normalise_EUVI_p(zero_point, EUVI_p, EUVI_dates)
    AIA_rolling_75p = moving_average(AIA_p[8], n)

    # normalise AIA data
    normalise_data("AIA", AIA_rolling_75p, clip_max, AIA_outlier_i, 0)

    # normalise EUVI data
    normalise_data("EUVI", EUVI_rolling_75p, clip_max, EUVI_outlier_i, zero_point)
