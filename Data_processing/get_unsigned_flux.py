from pixel_area import get_pixel_areas
import numpy as np
from astropy.io import fits
import os
from sql_util import create_connection, execute_read_query
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


def get_flux(data, save_path):
    fluxes = []
    dates = []
    for path, date in data:
        if path in [None, "NULL"]:
            continue
        
        data = np.load(path)

        # undo normalisation
        data = np.abs(data)**2
        data *= clip_max
        flux = area * np.absolute(data)

        # remove nans
        flux = np.nan_to_num(flux)

        total_flux = np.sum(flux)

        fluxes.append(total_flux)
        dates.append(date)
    
    np.save(save_path, [fluxes, dates])

save_dir = f"Data/unsigned_flux/"
os.makedirs(save_dir) if not os.path.exists(save_dir) else None

shape = (1024, 1024)
clip_max = np.load("Data/np_objects/HMI_clip_max.npy")
euvi_dir = "Data/fits_EUVI/"
header_ref = f"{euvi_dir}{os.listdir(euvi_dir)[0]}"
connection = create_connection("./image.db")


# get pixel area
hdul = fits.open(header_ref, memmap=False, ext=0)
hdul.verify("fix")
header = hdul[0].header
# radius of sun in arcsec
r_sun_arc = header["RSUN"]
# radius of sun in pixels
r_sun_pix = [0.5 * shape[0], 0.5 * shape[1]]
# width of pixel in arcsec
cdelt = [r_sun_arc/r_sun_pix[0], r_sun_arc/r_sun_pix[1]]
# reference pixel
c_ref = [0.5 * shape[0], 0.5 * shape[1]]

area = get_pixel_areas(header, shape, cdelt, c_ref)


for data_type in args.data:
    instrument, mode = data_type.split(".")
    save_path = f"{save_dir}flux_{instrument}_{mode}"
    print(f"Getting unsignd flux from {mode} in {instrument}.")
    get_paths = f"""
        SELECT
            {mode},
            date
        FROM
            {instrument}
    """
    data = execute_read_query(connection, get_paths)
    get_flux(data, save_path)
