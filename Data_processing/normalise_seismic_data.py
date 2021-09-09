import os
from datetime import datetime
import numpy as np
import cv2

q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]
percentiles = np.load(f"Data/np_objects/phase_map_percentiles.npy").T
dates = np.load(f"Data/np_objects/phase_map_dates.npy", allow_pickle=True)
w = h = 1024

abs_max = abs(np.max(percentiles[-1]))
abs_min = abs(np.min(percentiles[0]))

print(f"Absolute max: {abs_max}, Absolute min: {abs_min}")

clip_max = np.max([abs_max, -abs_min])
# to get data between -0.5 and 0.5, and centered about 0
noramlisation_factor = 1.0/(clip_max * 2)

np_dir = f"Data/np_phase_map/"
normal_np_dir = f"Data/np_phase_map_normalised/"
if not os.path.exists(normal_np_dir):
    os.makedirs(normal_np_dir)

data = np.sort(os.listdir(np_dir))

# normal percentiles and corresponding dates
normal_p = []
normal_d = []


for i, (name, date, p) in enumerate(zip(data, dates, percentiles)):
    save_name = f'phase_map_{date.year}.{date.month:0>2}.{date.day:0>2}_' \
                f'{date.hour:0>2}:{date.minute:0>2}:{date.second:0>2}'
    filename = np_dir + name
    img = np.load(filename)

    img = img * noramlisation_factor
    img += 0.5
    try:
        img = cv2.resize(img, dsize=(w, h))
        np.save(normal_np_dir + name, img)
        percentiles = np.nanpercentile(img, q)
        if percentiles is not None:
            normal_p.append(percentiles)
            normal_d.append(date)
    except cv2.error as e:
        print(f"{name}: {e}")
    except IndexError as e:
        print(f"{name}: {e}")


percentile_dir = "Data/np_objects/"
os.makedirs(percentile_dir) if not os.path.exists(percentile_dir) else None

np.save(f"{percentile_dir}phase_map_normal_percentiles", normal_p)
np.save(f"{percentile_dir}phase_map_normal_dates", normal_d)
