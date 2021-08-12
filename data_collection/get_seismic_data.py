import requests  # to get image from the web
import shutil  # to save it locally
from datetime import timedelta, datetime
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--start",
                    help="start date",
                    default='2010-04-24 00:00:00')
parser.add_argument("--end",
                    help="end date",
                    default='2020-01-01 00:00:00')
args = parser.parse_args()

start = args.start
end = args.end


# Set up the image URL and filename
main_url = "http://jsoc.stanford.edu/data/farside/Phase_Maps/"

# files are formated as: PHASE_MAP_yyyy.mm.dd_hh:mm:ss.fits
start_date = datetime.fromisoformat(start)
end_date =datetime.fromisoformat(end)
dt = timedelta(hours=12)

folder = "./Data/fits_phase_map/"
os.makedirs(folder) if not os.path.exists(folder) else None

# http://jsoc.stanford.edu/data/farside/Phase_Maps/2010/PHASE_MAP_2010.04.25_00:00:00.fits
date = start_date
while date <= end_date:
    print(f"{date}\r", end="")
    name = f"PHASE_MAP_{date.year}.{date.month:0>2}." \
           f"{date.day:0>2}_{date.hour:0>2}:00:00.fits"

    url = f'{main_url}/{date.year}/{name}'
    filename = folder + name
    # Open the url image and stream content.
    r = requests.get(url, stream=True)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        r.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    else:
        print(f'{name} Couldn\'t be retreived')

    date += dt
