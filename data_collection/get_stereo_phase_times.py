import numpy as np
# import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import urllib.request  # the lib that handles the url stuff

# combine all stereo data into array: data
start_date = datetime(2010, 4, 25)

end_date = datetime(2020, 8, 3)


folder = "Data/np_objects/"
os.makedirs(folder) if not os.path.exists(folder) else None
data = np.array([], dtype=float).reshape(0, 7)

for year in range(2010, 2020):
    print(f"Getting data from {year}")
    url = f"http://www.srl.caltech.edu/STEREO2/Position/ahead/" \
          f"position_ahead_{year}_HEEQ.txt"
    response = urllib.request.urlopen(url)
    new_data = np.loadtxt(response)
    data = np.concatenate((data, new_data))


"""
year: yyyy
doy: day-of-year (counting from 1)
second: is the second-of-day
flag: 0 if the data are predictive, 1 if the data are definitive
x, y, z: coords
"""
year, doy, second, flag, x, y, z = data.T

# get date time from year, doy, second
year = year.astype(int)
year = np.array([datetime(year=y, month=1, day=1) for y in year])

doy = doy.astype(int)
second = second.astype(int)
dt = np.array((doy, second)).T
dt = np.array([timedelta(days=d.item(), seconds=s.item()) for d, s in dt])

stereo_time = year + dt

# angle between acoustic image and stereo A (radians)
angle = np.arctan2(-y, -x)

# carrington rotation period (days)
period = 27.2753

# time difference between stereo and accoustic map (farside):
dt = angle * period / (2*np.pi)
# convert to timedelta
dt = np.array([timedelta(days=d) for d in dt])


# equivalent time for phase/accoustic maps
# (so that the active regions are in the same position):
phase_time = stereo_time - dt

date = start_date
dt = timedelta(hours=12)
# index for moving through phase and stereo time arrays
i = 0

phase_stereo_times = np.stack([phase_time, stereo_time], axis=1)
np.save(f"{folder}phase_stereo_times", phase_stereo_times)


# # convert to string:
# phase_time = np.array([time.strftime("%Y.%m.%d_%H:%M:%S")
#                       for time in phase_time])
# stereo_time = np.array([time.strftime("%Y.%m.%d_%H:%M:%S")
#                        for time in stereo_time])


# phase_stereo_times = np.stack((phase_time, stereo_time), axis=1)

# np.savetxt("DATA/phase_stereo_times.txt", phase_stereo_times, fmt='%s')


# plot data
# fig, ax = plt.subplots()

# ax.set_xlim(-1.5e8, 1.5e8)
# ax.set_ylim(-1.5e8, 1.5e8)
# ax.plot(data[-3], data[-2])
# plt.show()

# time_differences = [x.total_seconds()/3600 for x in (phase_time-stereo_time)]
# plt.plot_date(phase_time[::20], time_differences[::20],
# markersize=1)
# plt.xlabel("Year")
# plt.ylabel("Time difference (Hours) of an observation")
# plt.title("Stereo position vs the Farside of the Sun")
# plt.show()
