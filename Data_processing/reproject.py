import os
import numpy as np
from astropy.io import fits
from bisect import bisect_left
from datetime import datetime, timedelta
from shutil import copyfile, rmtree
from skimage.transform import warp
import matplotlib.pyplot as plt
import glob
import sqlite3
from sqlite3 import Error
from sql_util import create_connection, execute_query, execute_read_query

q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]

def get_stereo_header(filename):
    hdul = fits.open(filename, memmap=False, ext=0)
    hdul.verify("fix")
    stereo_header = hdul[0].header
    return stereo_header


def get_distance(theta_x, theta_y, D_0=200, R_0=1):
    # initialise d
    d = np.ones(theta_x.shape)

    cos_theta = np.sin(np.pi/2 - theta_y) * np.cos(theta_x)
    # descriminant in distance formula
    des = D_0**2 * cos_theta**2 - D_0**2 + R_0

    # if no solution (point not on sun) return Nan
    d[des < 0] = np.nan
    # use minus since we want the hemisphere facing us
    d *= D_0 * cos_theta - np.sqrt(D_0**2 * cos_theta**2 - D_0**2 + R_0)

    return d


def heliop_to_helioc(theta_x, theta_y, D_0=200):
    """
    Theta_x/y in arcsec
    d in solar radii
    """
    # convert to radians
    theta_y = theta_y * np.pi / (180 * 3600)
    theta_x = theta_x * np.pi / (180 * 3600)
    d = get_distance(theta_x, theta_y, D_0)
    x = d * np.cos(theta_y) * np.sin(theta_x)
    y = d * np.sin(theta_y)
    z = D_0 - d * np.cos(theta_y) * np.cos(theta_x)

    return (x, y, z)


def helioc_to_heliographic(x, y, z, B_0=0, Phi_0=0, R_0=1, L_0=0):
    r = R_0
    Theta = np.arcsin((y*np.cos(B_0) + z*np.sin(B_0))/r)
    Phi = Phi_0 + np.angle(z*np.cos(B_0) - y * np.sin(B_0) + x * 1.j)
    Phi_c = (Phi + L_0) % (2*np.pi)
    return (Theta, Phi_c)


def transformation(coord, r_sun=1200, D_0=200, R_0=1, B_0=0,  Phi_0=0, L_0=0):
    col = coord[:, 0]
    row = coord[:, 1]
    w = h = 1024
    # convert col and row to helioprojective arcsec
    theta_x = (col - w/2) * 2 * r_sun / w
    theta_y = (row - h/2) * 2 * r_sun / h

    # get heliocentric coords
    x, y, z = heliop_to_helioc(theta_x, theta_y, D_0=D_0)

    Theta, Phi_c = helioc_to_heliographic(x, y, z, B_0=B_0, Phi_0=Phi_0,
                                          R_0=R_0, L_0=L_0)

    col = Phi_c * 180 / np.pi
    row = (Theta + np.pi/2) * 180 / np.pi
    return np.stack((col, row), axis=-1)


def insert_into_db(connection, path, id):
    insert_path = f"""
    UPDATE
        phase_map
    SET
        np_path = "{path}"
    WHERE
        id = {id}
    """
    execute_query(connection, insert_path)

get_phase_map_paths = """
SELECT
    fits_path,
    date,
    id
FROM
    phase_map
"""

connection = create_connection("./image.db")
output = execute_read_query(connection, get_phase_map_paths)

# get stereo header for reference
stereo_fits_path = "Data/fits_EUVI/"
stereo_fits_path += os.listdir(stereo_fits_path)[0] 
stereo_header = get_stereo_header(stereo_fits_path)
D_0 = stereo_header["DSUN_OBS"] / 696340000  # in terms of radius
r_sun = stereo_header["RSUN"]
B_0 = 0 # helographic latitude
Phi_0 = 0

# percentiles
percentiles_lst = []
date_lst = []

# directory for reprojected phase maps:
output_dir = "Data/np_phase_map/"
os.makedirs(output_dir) if not os.path.exists(output_dir) else None

for phase_map_fits_path, date, id in output:
    hdul = fits.open(phase_map_fits_path, memmap=False, ext=0)
    hdul.verify("fix")
    smap_data = hdul[0].data
    smap_header = hdul[0].header

    # get parameters
    try:
        L_0 = smap_header["REF_L0"] * np.pi/180
        B_0 = smap_header["REF_B0"] * np.pi/180

    except TypeError:
        print(f"Missing args on {date}")
        continue

    map_args = {"r_sun": r_sun, "D_0": D_0, "R_0": 1,
                "B_0": B_0,  "Phi_0": Phi_0, "L_0": L_0}

    # transform seismic map to match stereo data:
    new_smap = warp(smap_data, transformation,
                    output_shape=(1024, 1024), map_args=map_args)

    new_path = f"{output_dir}PHASE_MAP_{date}.npy"

    np.save(new_path, new_smap)
    insert_into_db(connection, new_path, id)
    # get percentiles
    percentiles = np.percentile(new_smap, q)
    if percentiles is not None:
        percentiles_lst.append(percentiles)
        date_lst.append(date)


# save percentiles/dates
percentile_dir = "Data/np_objects/"
os.makedirs(percentile_dir) if not os.path.exists(percentile_dir) else None
dates = [datetime.strptime(date, "%Y.%m.%d_%H:%M:%S")
                    for date in date_lst]
np.save(f"{percentile_dir}phase_map_percentiles", percentiles_lst)
np.save(f"{percentile_dir}phase_map_dates", dates)
