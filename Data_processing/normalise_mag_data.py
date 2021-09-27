import os
from datetime import datetime
import numpy as np
import cv2

q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]
percentiles = np.load(f"Data/np_objects/HMI_percentiles.npy").T
w = h = 1024


def get_mask(size):
    w = h = size
    center = (int(w/2), int(h/2))
    radius = w/2 + 1
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    mask = dist_from_center <= radius
    return mask


mask = get_mask(w)

abs_max = abs(np.max(percentiles[-1]))
abs_min = abs(np.min(percentiles[0]))

print(f"Absolute max: {abs_max}, Absolute min: {abs_min}")

clip_max = np.max([abs_max, -abs_min])


np_dir = f"Data/np_HMI/"
normal_np_dir = f"Data/np_HMI_normalised/"
if not os.path.exists(normal_np_dir):
    os.makedirs(normal_np_dir)



data = np.sort(os.listdir(np_dir))

# normal percentiles and corresponding dates
normal_p = []
normal_d = []


for i in range(len(data)):
    name = data[i]
    if os.path.exists(f"{normal_np_dir}{name}.npy"):
         print(name + " already done.")
         continue
    print(name)
    date_str = name.split('_')
    date_str = date_str[1] + date_str[2]
    date = datetime.strptime(date_str, '%Y.%m.%d%H:%M:%S.npy')
    save_name = f'HMI_{date.year}.{date.month:0>2}.{date.day:0>2}_' \
                f'{date.hour:0>2}:{date.minute:0>2}:{date.second:0>2}'
    filename = np_dir + name
    img = np.load(filename)
    img = img/clip_max
    img = img.clip(-1, 1)
    img = np.sign(img)*(np.abs(img) ** (1/2))

    try:
        img = cv2.resize(img, dsize=(w, h))
        img *= mask

        np.save(normal_np_dir + name, img)
        percentiles = np.percentile(img, q)
        if percentiles is not None:
            normal_p.append(percentiles)
            normal_d.append(date)
    except cv2.error as e:
        print(f"{name}: {e}")
    except IndexError as e:
        print(f"{name}: {e}")


percentile_dir = "Data/np_objects/"
os.makedirs(percentile_dir) if not os.path.exists(percentile_dir) else None
np.save(f"{percentile_dir}HMI_clip_max", clip_max)
np.save(f"{percentile_dir}HMI_normal_percentiles", normal_p)
np.save(f"{percentile_dir}HMI_normal_dates", normal_d)