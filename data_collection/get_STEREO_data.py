from sunpy.net import Fido, attrs as a
from get_equivalent_time import get_stereo_time
from datetime import datetime, timedelta
import astropy.units as u  # for AIA
import argparse
import os

from sunpy.net.fido_factory import UnifiedResponse
from sunpy.net.vso.vso import QueryResponse

parser = argparse.ArgumentParser()
parser.add_argument("--start",
                    help="start date",
                    default='2010-01-11 00:00:00')
parser.add_argument("--end",
                    help="end date",
                    default='2020-01-01 00:00:00')
parser.add_argument("--cadence",
                    type=int,
                    default=12
                    )
parser.add_argument("--path",
                    help="directory to store data",
                    default='./Data/'
                    )
parser.add_argument("--email",
                    default="csmi0005@student.monash.edu")
args = parser.parse_args()

start = args.start
end = args.end
cadence = args.cadence
email = args.email

wavelength = 304*u.AA
source = 'STEREO_A'
instrument = 'EUVI'
path = f"{args.path}fits_STEREO/"
os.makedirs(path) if not os.path.exists(path) else None
cadence = timedelta(hours=cadence)
fmt = "%Y-%m-%d %H:%M:%S"

# start time for downloading
s_time = datetime.fromisoformat(start)
# time of end of downloading
f_time = datetime.fromisoformat(end)
# take data from 8 days at a time
step_time = timedelta(days=8)
# time of end of this step:
e_time = s_time + step_time
# time between searches


def get_index(all_times, stereo_times):
    index = []

    # index for all_times
    a_i = 0
    # index for stereo times
    s_i = 0

    # current all time:
    a_time = all_times[a_i]

    while a_i < len(all_times) and s_i < len(stereo_times):

        # stereo time:
        s_time = stereo_times[s_i]

        # previous and current all times
        p_time, a_time = a_time, all_times[a_i]

        if a_time == s_time:
            index.append(a_i)
            s_i += 1
            a_i += 1

        elif (a_time > s_time) or (a_i == len(all_times) - 1):
            # if the previous time was closer to current:
            if abs(s_time - p_time) < abs(s_time - a_time):
                a_time = p_time
                a_i = a_i-1
            if abs(s_time - a_time) <= timedelta(hours=1):
                index.append(a_i)
            s_i += 1

        a_i += 1

    return index


while True:
    if e_time > f_time:
        e_time = f_time

    phase_times = []
    t = s_time
    while t < e_time:
        phase_times.append(t)
        t += timedelta(hours=12)

    stereo_times = list(map(get_stereo_time, phase_times))

    # start time of stereo
    stereo_s_time = stereo_times[0]
    # end time of stereo
    stereo_e_time = stereo_times[-1]

    stereo_start = stereo_s_time.strftime("%Y-%m-%d %H:%M:%S")
    stereo_end = stereo_e_time.strftime("%Y-%m-%d %H:%M:%S")

    print(f"getting data between {stereo_start} and {stereo_end}")

    arg = [a.Wavelength(wavelength),
           a.vso.Source(source),
           a.Instrument(instrument),
           a.Time(stereo_start, stereo_end)]

    res = Fido.search(*arg)
    # get response object:
    table = res.tables[0]

    # get time string of final end time of results
    if len(table) == 0:
        print(f"{s_time} to {e_time}: Empty table")
        if e_time >= f_time:
            print("finish on empty table")
            break
        else:
            s_time = e_time
            e_time += step_time
            continue

    all_times = []
    for t in table["Start Time"]:
        t = t[0]
        # account for leap second in 2016
        if t == "2016-12-31 23:59:60":
            time = "2017-01-01 00:00:00"
        else:
            time = t
        all_times.append(datetime.strptime(time, fmt))

    index = get_index(all_times, stereo_times)

    # get response
    vso_response = list(res.responses)[0]
    block = vso_response._data

    block = [block[k] for k in index]

    q = QueryResponse(block)
    # build unified responce object from sliced query responce
    UR = UnifiedResponse(q)
    print(UR)
    downloaded_files = Fido.fetch(UR, path=path, progress=False)

    s_time = e_time
    if s_time == f_time:
        break
    e_time = s_time + step_time
