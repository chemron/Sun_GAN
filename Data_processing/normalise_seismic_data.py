import os
from datetime import datetime
import numpy as np
import cv2

q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]
dates = np.load(f"Data/np_objects/phase_map_dates.npy", allow_pickle=True)
w = h = 1024

abs_max = abs(np.max(percentiles[-1]))
abs_min = abs(np.min(percentiles[0]))

print(f"Absolute max: {abs_max}, Absolute min: {abs_min}")

clip_max = np.max([abs_max, -abs_min])
# to get data between -0.5 and 0.5, and centered about 0
noramlisation_factor = 1.0/(clip_max)

np_dir = f"Data/np_phase_map/"
normal_np_dir = f"Data/np_phase_map_normalised/"
if not os.path.exists(normal_np_dir):
    os.makedirs(normal_np_dir)

data = np.sort(os.listdir(np_dir))

# normal percentiles and corresponding dates
normal_p = []
normal_d = []

def get_mask(size):
    w = h = size
    center = (int(w/2), int(h/2))
    radius = w/2 + 1
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    mask = dist_from_center <= radius
    return mask

print(len(percentiles))
mask = get_mask(w)

for i, (name, date) in enumerate(zip(data, dates)):
    save_name = f'phase_map_{date.year}.{date.month:0>2}.{date.day:0>2}_' \
                f'{date.hour:0>2}:{date.minute:0>2}:{date.second:0>2}'
    filename = np_dir + name
    img = np.load(filename)

    img = img * noramlisation_factor
    try:
        img = cv2.resize(img, dsize=(w, h))
        img = np.nan_to_num(img)
        img *= mask
        np.save(normal_np_dir + name, img)
        percentiles = np.percentile(img, q)
        if percentiles is not None:
            normal_p.append(percentiles)
            normal_d.append(date)
        print(name)
    except cv2.error as e:
        print(f"{name}: {e}")
    except IndexError as e:
        print(f"{name}: {e}")


percentile_dir = "Data/np_objects/"
os.makedirs(percentile_dir) if not os.path.exists(percentile_dir) else None

np.save(f"{percentile_dir}phase_map_normal_percentiles", normal_p)
np.save(f"{percentile_dir}phase_map_normal_dates", normal_d)
