import os
import numpy as np
import sunpy
import sunpy.map
from astropy.io import fits
from datetime import datetime
from astropy.coordinates import SkyCoord
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--data",
                    help="name of data",
                    default='AIA'
                    )
args = parser.parse_args()

mode = args.data
fits_dir = f"Data/fits_{mode}/"
np_dir = f"Data/np_{mode}/"
os.makedirs(np_dir) if not os.path.exists(np_dir) else None
already_done = os.listdir(np_dir)
files = np.sort(os.listdir(fits_dir))
dates = []
# percentiles
q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]
p_w = 361  # width and height of phase maps
p_h = 180


def get_percentiles(filename):
    try:
        name = filename.strip(".fits").strip('.fts')
        if name + ".npy" in already_done:
            print(f"Already converted: {name}")
            data = np.load(f"{np_dir}{name}.npy").flatten()
        else:
            print(filename)

            if mode == 'phase_map':
                hdul = fits.open(fits_dir + filename, memmap=False, ext=0)
                hdul.verify("fix")

                data = hdul[0].data

                # cut off top:
                data = data[1:]

                # rotate if less than half of the top row is nan
                rotate = False
                if np.sum(np.isnan(data)[0]) < p_w//2:
                    rotate = True
                    data = np.rot90(data, 2)

                # location of nans in data
                nan_loc = np.where(np.isnan(data))

                # location of lowest nans in image
                low_nan = (nan_loc[0] == np.max(nan_loc[0]))
                low_nan_loc = np.where(low_nan)

                # collumns of lowest nans
                low_nan_x = nan_loc[1][np.min(low_nan_loc):np.max(low_nan_loc)]

                # if zero in low_nan_x then lowest nan's are split across edges
                if 0 in low_nan_x:
                    # number of nans on left edge
                    n = sum((low_nan_x < p_w//2))
                    # rearange so it's like (... , 360, 361, 0, 1, ...)
                    low_nan_x = np.concatenate((low_nan_x[n:], low_nan_x[:n]))

                # centre collumn of nans:
                centre = low_nan_x[len(low_nan_x)//2]

                # split into two parts along the centre of nans:
                split = np.hsplit(data,
                                    [centre]
                                    )

                # combine
                data = np.concatenate((split[1], split[0]), axis=1)

                # Rotate back if rotated earlier
                if rotate:
                    data = np.rot90(data, 2)

            else:
                # HMI or AIA
                map_ref = sunpy.map.Map(fits_dir + filename)

                # not necessary for percentiles
                mat = map_ref.rotation_matrix
                map_ref = map_ref.rotate(rmatrix=mat)

                # crop so only sun is shown
                radius = map_ref.rsun_obs
                top_right = SkyCoord(radius, radius,
                                        frame=map_ref.coordinate_frame)
                bottom_left = SkyCoord(-radius, -radius,
                                        frame=map_ref.coordinate_frame)
                submap = map_ref.submap(bottom_left, top_right=top_right)

                data = submap.data

            if data is not None:
                np.save(f"{np_dir}{name}", data)
                data = np.nan_to_num(data).flatten()
            else:
                return

        percentiles = np.percentile(data, q)
        if percentiles is not None:
            append_date(name)
            return percentiles
    except TypeError as err:
        print(f"TypeError:{filename}, {err}")
    except OSError as err:
        print(f"OSError:{filename}, {err}")
    except ValueError as err:
        print(f"ValueError:{filename}, {err}")
    except IndexError as err:
        print(f"IndexError:{filename}, {err}")
    return


def append_date(name):
    date_str = name.replace(".", "").replace(":", "")
    date_str = date_str.split("_")
    date_str = date_str[-2] + date_str[-1]
    dates.append(date_str)


files = np.sort(os.listdir(fits_dir))

percentiles = np.stack([p for f in files
                        if (p := get_percentiles(f)) is not None])

if len(percentiles) != len(dates):
    print(len(percentiles), len(dates))
    raise Exception("percentiles and dates have different sizes")

percentile_dir = "Data/np_objects/"
os.makedirs(percentile_dir) if not os.path.exists(percentile_dir) else None

dates = [datetime.strptime(date, "%Y%m%d%H%M%S")
                    for date in dates]
np.save(f"{percentile_dir}{mode}_percentiles", percentiles)
np.save(f"{percentile_dir}{mode}_dates", dates)
